import json as j
import os
import re
import copy
import datetime
from class_operation import Operation


class Storage:
    def __init__(self, Path = "data.json"):
        self.Path = Path
        self.temp_log = None

    def store_data(self, operation: Operation) -> None:
        # Leer datos existentes o lista vacía
        if os.path.exists(self.Path) and os.stat(self.Path).st_size > 0:
            with open(self.Path, "r", encoding="UTF-8") as f:
                data = j.load(f)
        else:
            data = []
        
        # Añadir nueva operación
        data.append(operation.to_dict())
        
        # Guardar todo
        with open(self.Path, "w", encoding="UTF-8") as f:
            j.dump(data, f, indent=4, default=str)



    def retrieve_data():
        None

    def update_data():
        None



op2 = Operation(2, "Sueldo", 1500.0, True, True, CreatedBy="EmpresaX")
storage = Storage()

storage.store_data(op2)