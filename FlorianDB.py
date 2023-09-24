import json
import os


class FlorianDB:
    def __init__(self, filename=None):
        self.db = {}
        self.filename = filename

    def load(self):
        if os.path.isfile(self.filename):
            self.db = json.load(open(self.filename, 'r'))
        else:
            self.db = {}

    def save(self):
        try:
            json.dump(self.db, open(self.filename, 'w+'))
            return True
        except:
            return False
