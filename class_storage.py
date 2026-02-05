import json as j
import os
import re
import pandas as pd
import datetime
from class_operation import Operation


class Storage:
    def __init__(self, Path = "data.json"):
        self.Path = Path
        self._data = []
        self.temp_log = None

    def __enter__(self): #carga los datos en memoria cuando se llama 
        self.load()

    def __exit__(self): #guarda todos los cambios antes de cerrarse
        while True:
            confirmation = int(input("\nQuieres guardar los cambios antes de salir? 1 = Si, 0 = No\n"))
            if confirmation == 1:
                self.save()
                break
            elif confirmation == 0:
                break



    def load(self): #carga los datos en el atributo _data      
        if os.path.exists(self.Path) and os.stat(self.Path).st_size > 0:
            with open(self.Path, "r", encoding="UTF-8") as f:
                self._data = j.load(f)
        else:
            self._data = []



    def save(self): #guarda los cambios en los datos en memoria
        with open(self.Path, "w", encoding="UTF-8") as f:
            j.dump(self._data, f, indent=4, default=str)
        
        print("\n Todos los datos han sido guardados \n")



    def store_log(self, operation: Operation) -> None: #almacena un elemento sin reescribir 
        self._data.append(operation.to_dict())
        


    def get_log(self, OperationID:int, logdate = None): #creo que logdate es necesario para diferenciar entre recursivos
        if logdate is None:
            for log in self._data:
                if log["ID"] == OperationID:
                    return log
            return None
        else:
            for log in self._data: 
                if (log["ID"] == OperationID) and (log["Fecha_Creacion"] == logdate):
                    return log
            return None




    def remove_log(self, logID):
        log = self.get_log(logID)
        if log:
            if log["Recursivo"] == False:
                confirmation =  input(f"Se va a borrar la operación {log}. \n ¿Quieres continuar? y/n \n ")

                if confirmation.lower() == "y":
                    self.remove_normal_log(log)
                    print()
                else:
                    print("Operación abortada \n")
                    return
                    
            elif log["Recursivo"] == True:
                self.reset_temp_log()
                self.filter(ID=logID)
                confirmation = int(input("¿Quieres borrar todas las operaciones futuras (0) o una operación concreta (1)? \n"))
                self.remove_recursive_log(log, confirmation)
            
            else:
                print("Operación corrupta.")
                self.remove_normal_log(log)


    def remove_normal_log (self, log: dict):
        self._data.remove(log)
        print(f"La operación '{log['ID']}: {log['Concepto']}' ({log['Importe']}) creada el {log['Fecha_Creacion']} ha sido eliminada")

        # Actualizar temp_log si existe y contiene el log eliminado
        if self.temp_log is not None:
            self.temp_log = self.temp_log[
                ~((self.temp_log["ID"] == log["ID"]) & (self.temp_log["Fecha_Creacion"] == log["Fecha_Creacion"]))
            ]

        
    def remove_recursive_log(self, log: dict, confirmation):
        today = datetime.date.today()
        if confirmation == 0:
            for _, entry in self.temp_log.iterrows():
                if entry["Fecha_Creacion"] > today:
                    delete_log = self.get_log(entry["ID"])
                    if delete_log:
                        self.remove_normal_log(delete_log)
                    else:
                        print(f"No se encontró la operación con ID {entry['ID']} y Fecha {entry['Fecha_Creacion']}")

        elif confirmation == 1:
            while True:
                fechastr = input("Introduce la fecha de la operación a eliminar (formato YYYY-MM-DD, o 'q' para cancelar): ")
                fechastr = re.sub(r"\s+", "", fechastr)

                if fechastr.lower() == "q":
                    print("Cancelando operación...\n")
                    return

                try:
                    fecha = datetime.datetime.strptime(fechastr, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Formato de fecha inválido. Inténtalo de nuevo o presiona 'q' para cancelar.")

            delete_log = self.get_log(log["ID"], fecha)
            if delete_log:
                self.remove_normal_log(delete_log)
            else:
                print(f"No se encontró ninguna operación con ID {log['ID']} en la fecha {fecha}.")
        else:
            print("Operación abortada \n")

    
    def view_logs(self, show_columns=None, reset=False):

        if reset:
            self.temp_log = None
            print("\nReseteando filtros...")

        elif self.temp_log is not None and not self.temp_log.empty:
            print("\nMostrando vista filtrada")

        else:
            print("\nMostrando todos los logs")

        if not self._data:
            print("Todavía no se ha registrado ninguna operación")
            return

        if (self.temp_log is not None) and not reset and not self.temp_log.empty:
            df = pd.DataFrame(self.temp_log)

        else:
            df = pd.DataFrame(self._data)

        df = df.sort_values('Fecha_Creacion', ascending=True)
        base_columns = ["ID", "Concepto", "Fecha_Creacion", "Fecha_Ejecucion", "Importe"]
        if show_columns == "*":
            showing_columns = base_columns + ["Recursivo", "Destinatario", "Usuario"]

        elif show_columns:
            showing_columns = base_columns + [col for col in show_columns if col not in base_columns]

        else:
            showing_columns = base_columns

        final_columns = [col for col in showing_columns if col in df.columns]
        print("\n", df[final_columns], "\n")


    def filter(self, **criteria):
        if not self._data:
            print("Aún no se han añadido operaciones")
            return pd.DataFrame()

        df = pd.DataFrame(self._data)
        for key, value in criteria.items():
            if key not in df.columns:
                print(f"Advertencia: La columna '{key}' no existe")
                continue

            df = df[df[key] == value]

        self.temp_log = df
        self.view_logs(show_columns=list(criteria.keys()), reset=False)


    def reset_temp_log(self):
        self.temp_log = None


    def nuke(self): ##TODO Añadir confirmacion extra 
        self._data = []
        self.save()
        print("A TOMAR POR CULO EL JSON")

if __name__ == "__main__":


    # print("Iniciando Prueba: \n")
    # storage = Storage()

    # op1 = Operation(1, "Pago Luz", 100.0, False, False, To="Endesa", CreatedBy="Usuario1")
    # op2 = Operation(2, "Sueldo", 1500.0, True, True, CreatedBy="EmpresaX")
    # op3 = Operation(4, "Pago Luz", 100.0, False, False, To="Endesa", CreatedBy="Usuario1")

    # storage.store_log(op1)
    # storage.store_log(op2)
    # storage.store_log(op3)


    # storage.view_logs(show_columns="*")
    # storage.filter(Recursivo=True, Concepto = "Sueldo", Importe = 1500)
    # print("procediendo al borrado")
    # storage.remove_log(4)

    # print("Data restante:")
    # storage.view_logs("*", True)
     
    # #guardar solo lo restante en _data
    # storage.save()


#%%
    storage = Storage()
    storage.load()

    storage.view_logs("*")
    # storage.nuke()