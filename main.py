from flask import Flask, request, render_template, send_from_directory
from hashlib import sha256
from pathlib import Path
from time import time
from lib.store import StoreHandler,ShaExistsError,TokenExistsError
import atexit,json,os,random,string


file_upload_path = "./upload_dat/"
datastore_path = "./.store.json"
host = "http://127.0.0.1:8000/"


if os.path.exists(datastore_path): # load data store from store.json if exists
    with open(datastore_path, "r") as file:
        ds = json.load(file)
else:
    ds = {  "sha":[],
            "ip":[],
            "time":[],
            "token":[],
            "ext":[],
            "origfname":[],
    }
store = StoreHandler(ds)

def calculate_sha256(file_path):
    sha_hash = sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha_hash.update(chunk)
    return sha_hash.hexdigest()

def on_exit():
    try:
        with open(datastore_path) as file:
            file.truncate(0)
            json.dump(ds,file, "w")
    except Exception as e:
        print("Error: Failed to save JSON data, datastore wont be saved.")
        print(str(e))

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
            os.rename(spath, spath)
            r = {  "sha":calculate_sha256(spath),
                    "ip":request.remote_addr,
                "time":int(time()),
                "token":token,
                "ext":ext,
                "origfname":file.filename,
        }
            store.add_entry(r)
            print(f'Info: File({file.filename}) uploaded successfully from {request.remote_addr}')
            return host+r["token"]+r["ext"]
        except ShaExistsError:
            print(f'Info: possible Sha collision or reupload of {file.filename}, Handling({request.remote_addr})')
            r = store.get_rows_by_key_value("sha",r["sha"])[0]
            return host+r["token"]+r["ext"]
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