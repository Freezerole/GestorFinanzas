from class_operation import Operation
import pandas as pd
import datetime
import re
import copy

class Logs:
    def __init__(self, storage=None):
        # Si no se pasa storage, se crea uno temporal en memoria
        if storage is None:
            self.storage = {"operations": []}  # modo prueba
            self.data = self.storage["operations"]
            
        else:
            self.storage = storage
            self.data = self.storage.data["operations"]
        self.temp_log = None


    def add_log(self, operation):
        # Guarda la operación en formato diccionario
        self.data.append(operation.to_dict())
        if hasattr(self.storage, "save"):
            self.storage.save()

        
    def get_log(self, OperationID: int, logdate=None):
        if logdate is None:
            for log in self.data:
                if log["ID"] == OperationID:
                    return log
            return None
        else:
            for log in self.data:
                if (log["ID"] == OperationID) and (log["CreationDate"] == logdate):
                    return log
            return None

    def remove_normal_log(self, log: dict):
        self.data.remove(log)
        print(f"La operación '{log['ID']}: {log['Concept']}' ({log['Value']}) creada el {log['CreationDate']} ha sido eliminada")

        # Actualizar temp_log si existe y contiene el log eliminado
        if self.temp_log is not None:
            self.temp_log = self.temp_log[
                ~((self.temp_log["ID"] == log["ID"]) & (self.temp_log["CreationDate"] == log["CreationDate"]))
            ]


    def remove_recursive_log(self, log: dict, confirmation):
        today = datetime.date.today()
        if confirmation == 0:
            for _, entry in self.temp_log.iterrows():
                entry_date = datetime.date.fromisoformat(entry["CreationDate"])
                if entry_date > today:
                    delete_log = self.get_log(entry["ID"], entry["CreationDate"])
                    if delete_log:
                        self.remove_normal_log(delete_log)
                    else:
                        print(f"No se encontró la operación con ID {entry['ID']} y Fecha {entry['CreationDate']}")
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

            delete_log = self.get_log(log["ID"], fecha.isoformat())
            if delete_log:
                self.remove_normal_log(delete_log)
            else:
                print(f"No se encontró ninguna operación con ID {log['ID']} en la fecha {fecha}.")
        else:
            print("Operación abortada \n")


    def remove_log(self, logID: int):
        log = self.get_log(logID)
        if log:
            if log["Recursive"] == False:
                confirmation = input(f"Se va a borrar la operación {log}. \n ¿Quieres continuar? y/n \n ")

                if confirmation.lower() == "y":
                    self.remove_normal_log(log)
                    print()
                else:
                    print("Operación abortada \n")
                    return
                
            elif log["Recursive"] == True:
                self.reset_temp_log()
                self.filter(ID=logID)
                confirmation = int(input("¿Quieres borrar todas las operaciones futuras (0) o una operación concreta (1)? \n"))
                self.remove_recursive_log(log, confirmation)
            else:
                print("Operación corrupta.")
                self.remove_normal_log(log)


    def view_logs(self, show_columns=None, reset=False):

        if reset:
            self.temp_log = None
            print("\nMostrando todos los logs")

        elif self.temp_log is not None and not self.temp_log.empty:
            print("\nMostrando vista filtrada")

        else:
            print("\nMostrando todos los logs")

        if not self.data:
            print("Todavía no se ha registrado ninguna operación")
            return

        if (self.temp_log is not None) and not reset and not self.temp_log.empty:
            df = pd.DataFrame(self.temp_log)

        else:
            df = pd.DataFrame(self.data)

        df = df.sort_values('CreationDate', ascending=True)
        base_columns = ["ID", "Concept", "CreationDate", "EffectiveDate", "Value"]
        if show_columns == "*":
            showing_columns = base_columns + ["Recursive", "To", "CreatedBy"]

        elif show_columns:
            showing_columns = base_columns + [col for col in show_columns if col not in base_columns]

        else:
            showing_columns = base_columns

        final_columns = [col for col in showing_columns if col in df.columns]
        print("\n", df[final_columns], "\n")

    def filter(self, **criteria):
        if not self.data:
            print("Aún no se han añadido operaciones")
            return pd.DataFrame()

        df = pd.DataFrame(self.data)
        for key, value in criteria.items():
            if key not in df.columns:
                print(f"Advertencia: La columna '{key}' no existe")
                continue

            df = df[df[key] == value]

        self.temp_log = df
        self.view_logs(show_columns=list(criteria.keys()), reset=False)

    def reset_temp_log(self):
        self.temp_log = None

    


if __name__ == "__main__":
    print("Iniciando Prueba: \n")
    logs = Logs()
    op1 = Operation(1, "Pago Luz", 100.0, False, False, To="Endesa", CreatedBy="Usuario1")
    op2 = Operation(2, "Sueldo", 1500.0, True, True, CreatedBy="EmpresaX")

    logs.add_log(op1)
    logs.add_log(op2)

    logs.view_logs(show_columns="*")
    logs.filter(Recursive=True, Concept="Sueldo", Value=1500)
    print("procediendo al borrado")
    logs.remove_log(2)

    print("Data restante:")
    logs.view_logs("*", True)
