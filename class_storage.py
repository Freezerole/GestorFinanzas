import json 
import os

class Storage:
    def __init__(self, filename = "data"):
        self.filename = filename
        self.data = { "global" : {"last_id": 0}, "users": [], "operations": [] }
        self.load()
    
    def load(self):
        "Carga el archivo o, si no existe, genera uno nuevo"
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding= "utf-8") as f:
                self.data = json.load(f)

        else:
            self.save() #Crea un archivo vacio
    

    def save(self):
        "Guarda los datos en el archivo JSON"
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent= 4, ensure_ascii= False)
    
    
    def get_last_ID(self):
        return self.data["global"]["last_id"]
    
    
    def get_next_ID(self):
        self.data["global"]["last_id"] += 1
        self.save()
        return self.get_last_ID()
    

    def add_operation(self, operation_data):
        self.data["operations"].append(operation_data)
        self.save()


    def get_operations(self, user_id=None):
        if user_id is None:
            return self.data["operations"]
        return [op for op in self.data["operations"] if op["UserID"] == user_id]


    def add_user(self, name, real_balance=0.0, estimated_balance=0.0):
        "Añade un usuario y le asigna unos datos" #Identifica mediante ID, no esta relacionado con las operaciones"  TODO
        new_id = len(self.data["users"]) + 1
        user = { "id": new_id, "name": name, "real_balance": real_balance, "estimated_balance": estimated_balance}
        self.data["users"].append(user)
        self.save()

        return user


    def get_users(self):
        return self.data["users"]
    
