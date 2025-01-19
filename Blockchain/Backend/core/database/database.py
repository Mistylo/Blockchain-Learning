import os
import json

class BaseDB:
    def __init__(self):
        self.basepath = 'data'
        self.filepath = '/'.join((self.basepath, self.filename))
    
    def read(self):
        if not os.path.exists(self.filepath):
            print(f"File {self.filepath} not found. Returning empty list.")
            return []

        with open(self.filepath, 'r') as file:
            raw = file.readline().strip()

        if not raw:  
            print(f"File {self.filepath} is empty. Returning empty list.")
            return []

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file {self.filepath}. Returning empty list.")
            return []

        return data


    def write(self, item):
        data = self.read()
        if not data:  
            data = []
        data = data + item
        with open(self.filepath, "w+") as file:
            file.write(json.dumps(data))


class BlockchainDB(BaseDB):
    def __init__(self):
        self.filename = "blockchain"
        super().__init__()

    def lastBlock(self):
        data = self.read()
        if data:  
            return data[-1]
        print("Blockchain is empty. Returning None.")
        return None
    
    
class AccountDB(BaseDB):
    def __init__(self):
        self.filename = "account"
        super().__init__()