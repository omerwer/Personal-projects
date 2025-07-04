import json
import os

class JSONDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.data = self._load_db()

    def _load_db(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                return json.load(f)
        return {"participants": {}}

    def _save_db(self):
        with open(self.db_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def update(self, keys, value):
        d = self.data
        for key in keys[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value
        self._save_db()
