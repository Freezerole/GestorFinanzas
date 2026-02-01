import json as j
import os
from class_operation import Operation


class Storage:
    def __init__(self, Path = "data.json"):
        self.Path = Path

    def store_data(self, operation: Operation) -> None:
        #si no existe, lo crea 
        if not os.path.exists(self.Path) or os.stat(self.Path).st_size == 0:
            with open(self.Path, "w") as f:
                j.dump([], f)
        
        #una vez garantizado su existencia: 
        with open(self.Path, "r") as f: 
            datos  = j.load(f)

        