import json

class Config:
    def __init__(self, config_path:str):
        self.config = json.load(open(config_path, "r"))
        
    def get_config(self):
        return self.config