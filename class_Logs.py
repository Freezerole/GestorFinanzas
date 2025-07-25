from class_operation import Operation
import pandas as pd
import datetime
import re
import copy

class Logs:
    def __init__(self):
        self.data = []
        self.temp_log = None

    def add_log(self, operation: Operation):
        datalog = {
            "ID": operation.ID,
            "Concepto": operation.Concept,
            "Importe": operation.signed_value,
            "IsIncome": operation.IsIncome,
            "Destinatario": operation.To,
            "Recursivo": operation.Recursive,
            "Usuario": operation.CreatedBy,
            "Fecha_Creacion": operation.CreationDate,
            "Fecha_Ejecucion": operation.EffectiveDate,
            "Operacion": copy.deepcopy(operation)
        }
        self.data.append(datalog)

    def get_log(self, OperationID: int, logdate=None):
        if logdate is None:
            for log in self.data:
                if log["ID"] == OperationID:
                    return log
            return None
        else:
            for log in self.data:
                if (log["ID"] == OperationID) and (log["Fecha_Creacion"] == logdate):
                    return log
            return None

    def remove_normal_log(self, log: dict):
        self.data.remove(log)
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
                    delete_log = self.get_log(entry["ID"], entry["Fecha_Creacion"])
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


    def remove_log(self, logID: int):
        log = self.get_log(logID)
        if log:
            if log["Recursivo"] == False:
                confirmation = input(f"Se va a borrar la operación {log}. \n ¿Quieres continuar? y/n \n ")

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

    def add_recursive(self, interval: int, end: datetime):
        recursive_operation = gestor.add_operation()
        i = 0
        while (recursive_operation.EffectiveDate <= end) and (i <= 365):
            self.add_log(recursive_operation)
            recursive_operation = gestor.add_operation()
            i += 1

        if i == 365:
            print("Se ha programado la operación 365 veces. Máximo alcanzado \n")
        else:
            print(f"Se ha programado la operación {i} veces \n")


if __name__ == "__main__":
    print("Iniciando Prueba: \n")
    logs = Logs()
    op1 = Operation(1, "Pago Luz", 100.0, False, False, To="Endesa", CreatedBy="Usuario1")
    op2 = Operation(2, "Sueldo", 1500.0, True, True, CreatedBy="EmpresaX")

    logs.add_log(op1)
    logs.add_log(op2)

    logs.view_logs(show_columns="*")
    logs.filter(Recursivo=True)
    print("procediendo al borrado")
    logs.remove_log(2)

    print("Data restante:")
    logs.view_logs("*", True)
