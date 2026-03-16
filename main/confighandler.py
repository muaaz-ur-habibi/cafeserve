import json

class Config:
    def __init__(self, config_path:str):
        self.config_path = config_path
        f = open(config_path, "r")
        self.config = json.load(f)
        f.close()
        
    def get_config(self):
        return self.config
    
    def set_config(self, updated_config:dict):
        f = open(self.config_path, "w")
        json.dump(updated_config, f, indent=4)
        f.close()

        return self.get_config()