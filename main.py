from flask import Flask, request, render_template, send_from_directory 
from hashlib import sha256
from pathlib import Path
from time import time
from lib.store import StoreHandler,ShaExistsError,TokenExistsError
import atexit,json,os,random,string


file_upload_path = "./upload_data/"
datastore_path = file_upload_path + ".store.json"

if os.path.exists(datastore_path): # load data store from store.json if exists
    with open(datastore_path, "r") as file:
        try:
            ds = json.load(file)
        except json.decoder.JSONDecodeError:
            print("Error: datastore seems corrupt, will be overwritten on write") 
            ds = { "sha":[],
            "ip":[],
            "time":[],
            "token":[],
            "ext":[],
            "origfname":[],
    }
else:
    ds = {  "sha":[],
            "ip":[],
            "time":[],
            "token":[],
            "ext":[],
            "origfname":[],
    }
store = StoreHandler(ds)

if os.path.exists(file_upload_path):
    pass
else:
    os.mkdir(file_upload_path)

def calculate_sha256(file_path):
    sha_hash = sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha_hash.update(chunk)
    return sha_hash.hexdigest()

def on_exit():
    try:
        if os.path.exists(datastore_path):
            file = open(datastore_path)
            file.truncate(0)
        else:
            file = open(datastore_path, "x")
        json.dump(ds,file)
    except Exception as e:
        print("Error: Failed to save JSON data, datastore wont be saved.")
        print(str(e))

def append_to_json_file():
    if os.path.exists(datastore_path):
        try:
            with open(datastore_path, 'r') as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            with open(datastore_path, 'w') as file:
                json.dump(ds, file, indent=4)
        except:
            print("Error: Failed to save JSON data, datastore wont be saved.")
        else:
            if isinstance(existing_data, list):
                existing_data.append(ds)
                updated_data = existing_data
            else:
                updated_data = [existing_data, ds]

            with open(datastore_path, 'w') as file:
                json.dump(updated_data, file, indent=4)

    else:
        with open(datastore_path, 'w') as file:
            json.dump(ds, file, indent=4)


app = Flask("fup")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file Provided'
        
        file = request.files['file']
        
        if file.filename == '':
            return 'No file Provided'
        try:
            token = ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(6))
            ext =  ''.join(Path(file.filename).suffixes)
            spath = file_upload_path+token+ext
            file.save(spath)
            r = {  "sha":calculate_sha256(spath),
                    "ip":request.remote_addr,
                "time":int(time()),
                "token":token,
                "ext":ext,
                "origfname":file.filename,
        }
            store.add_entry(r)
            print(f'Info: File({file.filename}) uploaded successfully from {request.remote_addr}')
            url = request.host_url+r["token"]+r["ext"]
            return render_template('copy.html', url=url)
        except ShaExistsError:
            os.remove(spath)
            print(f'Info: possible Sha collision or reupload of {file.filename}, Handling({request.remote_addr})')
            r = store.get_rows_by_key_value("sha",r["sha"])[0]
            url = request.host_url +r["token"]+r["ext"]
            return render_template('copy.html', url=url)
        except Exception as e:
            print("Error: "+ e )
    return render_template('upload.html')

@app.route('/<path:filename>')
def serve_file(filename):
    file = filename[0:6] + ''.join(Path(filename).suffixes)
    print("Debug:"+file+"|"+filename)
    return send_from_directory(file_upload_path, file)

atexit.register(on_exit)

if __name__ == '__main__':
    app.run(debug=True)