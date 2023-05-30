from time import time

class TokenExistsError(Exception):
    pass

class ShaExistsError(Exception):
    pass

class StoreHandler:
    def __init__(self, data):
        self.data = data

    def prune_old_entries(self):
        current_time = time()  # Current time in seconds since epoch
        one_year_ago = current_time - (365 * 24 * 60 * 60)  # One year ago in seconds

        for i in range(len(self.data["time"]) - 1, -1, -1):
            if self.data["time"][i] < one_year_ago:
                self.remove_entry(i)

    def remove_entry(self, index):
        for key in self.data:
            if index < len(self.data[key]):
                self.data[key].pop(index)

    def add_entry(self, entry):
        sha = entry.get("sha")
        token = entry.get("token")

        if sha in self.data["sha"]:
            raise ShaExistsError
        if token in self.data["token"]:
            raise TokenExistsError

        for key in self.data:
            if key in entry:
                self.data[key].append(entry[key])
            else:
                self.data[key].append(None)

    def get_rows_by_key_value(self, key, value):
        rows = []
        if key in self.data:
            for i in range(len(self.data[key])):
                if self.data[key][i] == value:
                    row = {}
                    for k in self.data:
                        row[k] = self.data[k][i]
                    rows.append(row)
        return rows

    def get_index_by_key_value(self, key, value):
        if key in self.data:
            for i in range(len(self.data[key])):
                if self.data[key][i] == value:
                    return i
        return None


