import json as j
import os
import re
import pandas as pd
import datetime
from class_operation import Operation


class Storage:
    def __init__(self, Path = "data.json"):
        self.Path = Path
        self.data = {"global": {"last_id": 0}, "operations": [], "users": []}
        self.temp_log = None

    def __enter__(self):  # carga los datos en memoria cuando se llama
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # guarda todos los cambios antes de cerrarse
        while True:
            confirmation = int(input("\nQuieres guardar los cambios antes de salir? 1 = Si, 0 = No\n"))
            if confirmation == 1:
                self.save()
                break
            elif confirmation == 0:
                break

    def load(self):  # carga los datos en el atributo data
        if os.path.exists(self.Path) and os.stat(self.Path).st_size > 0:
            with open(self.Path, "r", encoding="utf-8") as f:
                loaded = j.load(f)

            # Migración automática desde el formato antiguo (lista plana de operaciones)
            if isinstance(loaded, list):
                max_id = max((op.get("ID", 0) for op in loaded), default=0)
                self.data = {
                    "global": {"last_id": max_id},
                    "operations": loaded,
                    "users": []
                }
            else:
                self.data = loaded
                self.data.setdefault("global", {"last_id": 0})
                self.data.setdefault("operations", [])
                self.data.setdefault("users", [])
        else:
            self.data = {"global": {"last_id": 0}, "operations": [], "users": []}

    def save(self):  # guarda los cambios en los datos en memoria
        with open(self.Path, "w", encoding="utf-8") as f:
            j.dump(self.data, f, indent=4, default=str)

        print("\n Todos los datos han sido guardados \n")

    def get_next_id(self) -> int:  # genera y persiste el siguiente ID (reemplaza a IDGen)
        self.data["global"]["last_id"] += 1
        return self.data["global"]["last_id"]

    def add_log(self, operation: Operation) -> None:  # almacena una operación sin reescribir
        self.data["operations"].append(operation.to_dict())

    def get_log(self, OperationID: int, logdate=None):  # logdate diferencia entradas recursivas
        if logdate is None:
            for log in self.data["operations"]:
                if log["ID"] == OperationID:
                    return log
            return None
        else:
            for log in self.data["operations"]:
                if (log["ID"] == OperationID) and (log["CreationDate"] == logdate):
                    return log
            return None

    def remove_log(self, logID):
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

    def remove_normal_log(self, log: dict):
        self.data["operations"].remove(log)
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
                if entry["CreationDate"] > today:
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

        if not self.data["operations"]:
            print("Todavía no se ha registrado ninguna operación")
            return

        if (self.temp_log is not None) and not reset and not self.temp_log.empty:
            df = pd.DataFrame(self.temp_log)

        else:
            df = pd.DataFrame(self.data["operations"])

        df = df.sort_values('CreationDate', ascending=True)
        base_columns = ["ID", "Concept", "CreationDate", "EffectiveDate", "Value"]
        if show_columns == "*":
            showing_columns = base_columns + ["Recursive", "To", "CreatedBy"]

        elif show_columns:
            showing_columns = base_columns + [col for col in show_columns if col not in base_columns]

        else:
            showing_columns = base_columns

        final_columns = [col for col in showing_columns if col in df.columns]

        # Cabeceras en español solo para la impresión, el almacenamiento interno queda en inglés
        etiquetas_es = {
            "ID": "ID", "Concept": "Concepto", "CreationDate": "Fecha_Creacion",
            "EffectiveDate": "Fecha_Ejecucion", "Value": "Importe",
            "Recursive": "Recursivo", "To": "Destinatario", "CreatedBy": "Usuario",
            "IsIncome": "IsIncome",
        }
        df_mostrar = df[final_columns].rename(columns=etiquetas_es)
        print("\n", df_mostrar, "\n")

    def filter(self, **criteria):
        if not self.data["operations"]:
            print("Aún no se han añadido operaciones")
            return pd.DataFrame()

        # Traduce claves en español (las que usan main.py y Gestor) a las claves
        # internas en inglés que produce Operation.to_dict()
        traduccion = {
            "Concepto": "Concept", "Importe": "Value", "Destinatario": "To",
            "Recursivo": "Recursive", "Usuario": "CreatedBy",
            "Fecha_Creacion": "CreationDate", "Fecha_Ejecucion": "EffectiveDate",
        }
        criteria = {traduccion.get(k, k): v for k, v in criteria.items()}

        df = pd.DataFrame(self.data["operations"])
        for key, value in criteria.items():
            if key not in df.columns:
                print(f"Advertencia: La columna '{key}' no existe")
                continue

            df = df[df[key] == value]

        self.temp_log = df
        self.view_logs(show_columns=list(criteria.keys()), reset=False)


    def  list_operations(self, sort_by="CreationDate"):
        """Devuelve las operaciones ordenadas, sin imprimir nada. Para usar desde la API."""
        return sorted(self.data["operations"], key=lambda op: op[sort_by])

    def filter_operations(self, **criteria) -> list:
        """Versión de filter() sin pandas y sin print — devuelve la lista filtrada."""
        traduccion = {
            "Concepto": "Concept", "Importe": "Value", "Destinatario": "To",
            "Recursivo": "Recursive", "Usuario": "CreatedBy",
            "Fecha_Creacion": "CreationDate", "Fecha_Ejecucion": "EffectiveDate",
        }
        criteria = {traduccion.get(k, k): v for k, v in criteria.items()}

        results = self.data["operations"]
        for key, value in criteria.items():
            results = [op for op in results if op.get(key) == value]
        return results

    def remove_operation(self, op_id: int, creation_date=None) -> bool:
        """Borra UNA entrada por ID (+ fecha opcional, útil si el ID se repite
        en una serie recursiva). Sin confirmación por input() — la API decide
        si confirma o no antes de llamar a esto. Devuelve True/False."""
        log = self.get_log(op_id, creation_date)
        if log is None:
            return False
        self.remove_normal_log(log)
        return True

    def remove_operation_family(self, op_id: int) -> int:
        """Borra TODAS las entradas que compartan ese ID (toda una serie
        recursiva). Devuelve cuántas se borraron."""
        matches = [log for log in self.data["operations"] if log["ID"] == op_id]
        for log in matches:
            self.data["operations"].remove(log)
        return len(matches)

    def reset_temp_log(self):
        self.temp_log = None

    def nuke(self):  # TODO: añadir confirmación extra (ej. escribir "ELIMINAR")
        self.data = {"global": {"last_id": 0}, "operations": [], "users": []}
        self.save()
        print("A TOMAR POR CULO EL JSON")


# if __name__ == "__main__":

    # print("Iniciando Prueba: \n")
    # storage = Storage()

    # op1 = Operation(1, "Pago Luz", 100.0, False, False, To="Endesa", CreatedBy="Usuario1")
    # op2 = Operation(2, "Sueldo", 1500.0, True, True, CreatedBy="EmpresaX")
    # op3 = Operation(3, "Pago Luz", 100.0, False, False, To="Endesa", CreatedBy="Usuario1")

    # storage.add_log(op1)
    # storage.add_log(op2)
    # storage.add_log(op3)

    # storage.view_logs(show_columns="*")
    # storage.filter(Recursivo=True, Concepto="Sueldo", Importe=1500)
    # print("procediendo al borrado")
    # storage.remove_log(3)

    # print("Data restante:")
    # storage.view_logs("*", True)

    # print(f"Siguiente ID disponible: {storage.get_next_id()}")

    # # guardar solo lo restante
    # storage.save()