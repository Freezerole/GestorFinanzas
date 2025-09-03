from class_operation import Operation
import pandas as pd
import datetime
import re

class Logs:
    def __init__(self, storage=None):
        if storage is None:
            # Modo prueba sin persistencia
            self.storage = None
            self.data = []
        else:
            self.storage = storage
            self.data = self.storage.data["operations"]
        
        self.temp_log = None

    def add_log(self, operation: Operation):
        """Añade una operación al log y la guarda automáticamente"""
        operation_dict = operation.to_dict()
        
        if self.storage is None:
            # Modo prueba
            self.data.append(operation_dict)
        else:
            # Modo con persistencia - usa el método de Storage
            self.storage.add_operation(operation_dict)

    def get_log(self, operation_id: int, log_date=None):
        """Busca una operación por ID y opcionalmente por fecha"""
        if log_date is None:
            for log in self.data:
                if log["ID"] == operation_id:
                    return log
            return None
        else:
            # Convertir log_date a string si es necesario
            if isinstance(log_date, datetime.date):
                log_date = log_date.isoformat()
            
            for log in self.data:
                if (log["ID"] == operation_id) and (log["CreationDate"] == log_date):
                    return log
            return None

    def remove_normal_log(self, log: dict):
        """Elimina una operación normal y actualiza persistencia"""
        if self.storage is None:
            # Modo prueba
            if log in self.data:
                self.data.remove(log)
        else:
            # Modo con persistencia
            self.storage.remove_operation(log)
        
        print(f"La operación '{log['ID']}: {log['Concept']}' ({log['Value']}€) creada el {log['CreationDate']} ha sido eliminada")

        # Actualizar temp_log si existe y contiene el log eliminado
        if self.temp_log is not None and not self.temp_log.empty:
            self.temp_log = self.temp_log[
                ~((self.temp_log["ID"] == log["ID"]) & (self.temp_log["CreationDate"] == log["CreationDate"]))
            ]

    def remove_recursive_log(self, log: dict, confirmation):
        """Elimina operaciones recursivas según la opción elegida"""
        today = datetime.date.today()
        
        if confirmation == 0:
            # Eliminar todas las operaciones futuras
            for _, entry in self.temp_log.iterrows():
                try:
                    entry_date = datetime.date.fromisoformat(entry["CreationDate"])
                    if entry_date > today:
                        delete_log = self.get_log(entry["ID"], entry["CreationDate"])
                        if delete_log:
                            self.remove_normal_log(delete_log)
                        else:
                            print(f"No se encontró la operación con ID {entry['ID']} y Fecha {entry['CreationDate']}")
                except ValueError:
                    print(f"Fecha inválida en operación ID {entry['ID']}")
                    
        elif confirmation == 1:
            # Eliminar una operación específica
            while True:
                fecha_str = input("Introduce la fecha de la operación a eliminar (formato YYYY-MM-DD, o 'q' para cancelar): ")
                fecha_str = re.sub(r"\s+", "", fecha_str)

                if fecha_str.lower() == "q":
                    print("Cancelando operación...\n")
                    return

                try:
                    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Formato de fecha inválido. Inténtalo de nuevo o presiona 'q' para cancelar.")

            delete_log = self.get_log(log["ID"], fecha)
            if delete_log:
                self.remove_normal_log(delete_log)
            else:
                print(f"No se encontró ninguna operación con ID {log['ID']} en la fecha {fecha}.")
        else:
            print("Operación abortada\n")

    def remove_log(self, log_id: int):
        """Elimina operaciones por ID, manejando recursivas y normales"""
        log = self.get_log(log_id)
        if log:
            if not log["Recursive"]:
                confirmation = input(f"Se va a borrar la operación {log}. \n¿Quieres continuar? y/n\n")

                if confirmation.lower() == "y":
                    self.remove_normal_log(log)
                    print()
                else:
                    print("Operación abortada\n")
                    
            else:
                self.reset_temp_log()
                self.filter(ID=log_id)
                
                if self.temp_log is not None and not self.temp_log.empty:
                    try:
                        confirmation = int(input("¿Quieres borrar todas las operaciones futuras (0) o una operación concreta (1)?\n"))
                        self.remove_recursive_log(log, confirmation)
                    except ValueError:
                        print("Opción inválida. Operación cancelada.")
                else:
                    print("No se encontraron operaciones recursivas con ese ID.")
        else:
            print(f"No se encontró ninguna operación con ID {log_id}")

    def view_logs(self, show_columns=None, reset=False):
        """Visualiza los logs con opción de filtrado"""
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

        # Decidir qué datos mostrar
        if (self.temp_log is not None) and not reset and not self.temp_log.empty:
            df = self.temp_log.copy()
        else:
            df = pd.DataFrame(self.data)

        if df.empty:
            print("No hay datos para mostrar")
            return

        # Ordenar por fecha de creación
        df = df.sort_values('CreationDate', ascending=True)
        
        # Definir columnas a mostrar
        base_columns = ["ID", "Concept", "CreationDate", "EffectiveDate", "Value"]
        
        if show_columns == "*":
            showing_columns = base_columns + ["Recursive", "To", "CreatedBy"]
        elif show_columns and isinstance(show_columns, list):
            showing_columns = base_columns + [col for col in show_columns if col not in base_columns]
        else:
            showing_columns = base_columns

        # Filtrar solo las columnas que existen en el DataFrame
        final_columns = [col for col in showing_columns if col in df.columns]
        
        print("\n", df[final_columns].to_string(index=False), "\n")

    def filter(self, **criteria):
        """Filtra operaciones según criterios dados"""
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
        
        if not df.empty:
            # Mostrar solo las columnas relevantes para el filtro
            filter_columns = list(criteria.keys())
            self.view_logs(show_columns=filter_columns, reset=False)
        else:
            print("No se encontraron operaciones que coincidan con los criterios")

    def reset_temp_log(self):
        """Resetea el log temporal para mostrar todos los datos"""
        self.temp_log = None

    def get_dataframe(self):
        """Obtiene un DataFrame de pandas con todas las operaciones"""
        if not self.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.data)
        
        # Convertir fechas de string a datetime para análisis
        if 'CreationDate' in df.columns:
            df['CreationDate'] = pd.to_datetime(df['CreationDate'])
        if 'EffectiveDate' in df.columns:
            df['EffectiveDate'] = pd.to_datetime(df['EffectiveDate'])
            
        # Añadir columna de valor con signo para cálculos
        if 'Value' in df.columns and 'IsIncome' in df.columns:
            df['signed_value'] = df.apply(
                lambda row: row['Value'] if row['IsIncome'] else -row['Value'], 
                axis=1
            )
        
        return df


# Código de prueba
if __name__ == "__main__":
    print("Iniciando Prueba:\n")
    logs = Logs()
    
    op1 = Operation(1, "Pago Luz", 100.0, False, False, To="Endesa", CreatedBy="Usuario1")
    op2 = Operation(2, "Sueldo", 1500.0, True, True, CreatedBy="EmpresaX")

    logs.add_log(op1)
    logs.add_log(op2)

    logs.view_logs(show_columns="*")
    logs.filter(Recursive=True, Concept="Sueldo", Value=1500.0)
    
    print("Procediendo al borrado...")
    logs.remove_log(2)

    print("Data restante:")
    logs.view_logs("*", True)
