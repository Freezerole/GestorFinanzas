import json 
import os
import datetime

class Storage:
    def __init__(self, filename="data.json"):
        self.filename = filename
        self.data = {
            "global": {"last_id": 0}, 
            "users": [], 
            "operations": []
        }
        self.load()
    
    def load(self):
        """Carga el archivo o, si no existe, genera uno nuevo"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    # Validar estructura básica
                    if isinstance(loaded_data, dict) and "global" in loaded_data:
                        self.data = loaded_data
                    else:
                        print("Archivo de datos corrupto, creando nuevo...")
                        self.save()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error cargando datos: {e}. Creando archivo nuevo...")
                self.save()
        else:
            self.save()  # Crear archivo vacío
    
    def save(self):
        """Guarda los datos en el archivo JSON"""
        try:
            # Crear backup si el archivo existe
            if os.path.exists(self.filename):
                backup_name = f"{self.filename}.backup"
                with open(self.filename, 'r', encoding='utf-8') as original:
                    with open(backup_name, 'w', encoding='utf-8') as backup:
                        backup.write(original.read())
            
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False, default=str)
        except IOError as e:
            print(f"Error guardando datos: {e}")
    
    def get_last_id(self):
        """Obtiene el último ID usado"""
        return self.data["global"]["last_id"]
    
    def get_next_id(self):
        """Genera y guarda el próximo ID disponible"""
        self.data["global"]["last_id"] += 1
        self.save()
        return self.data["global"]["last_id"]
    
    def add_operation(self, operation_data):
        """Añade una operación y guarda automáticamente"""
        self.data["operations"].append(operation_data)
        self.save()
    
    def get_operations(self, user_id=None):
        """Obtiene operaciones, opcionalmente filtradas por usuario"""
        if user_id is None:
            return self.data["operations"]
        return [op for op in self.data["operations"] if op.get("UserID") == user_id]
    
    def remove_operation(self, operation_data):
        """Elimina una operación específica"""
        if operation_data in self.data["operations"]:
            self.data["operations"].remove(operation_data)
            self.save()
            return True
        return False
    
    # Funciones de usuario para futuro uso
    def add_user(self, name, real_balance=0.0, estimated_balance=0.0):
        """Añade un usuario y le asigna datos básicos"""
        new_id = len(self.data["users"]) + 1
        user = {
            "id": new_id, 
            "name": name, 
            "real_balance": real_balance, 
            "estimated_balance": estimated_balance,
            "created_date": datetime.date.today().isoformat()
        }
        self.data["users"].append(user)
        self.save()
        return user
    
    def get_users(self):
        """Obtiene lista de todos los usuarios"""
        return self.data["users"]
    
    def nuke(self):
        """Elimina todos los datos y reinicia el sistema"""
        self.data = {
            "global": {"last_id": 0}, 
            "users": [], 
            "operations": []
        }
        self.save()
        print("Sistema reiniciado completamente.")
