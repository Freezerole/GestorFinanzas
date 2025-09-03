from class_operation import Operation
from class_logs import Logs
from class_storage import Storage
import datetime
from dateutil.relativedelta import relativedelta  
import pandas as pd

#TODO:
"""
        Crear una funcion que genere por inputs las operaciones DONE
        Recursiva y normal (Ganancias y Perdidas) DONE
    Guardar datos del usuario (Nombre, Dinero, Nº Operaciones (Entre x e y Fechas) )
        Tracker del dinero que lleva DONE 
        Tracker del dinero que piensa gastar x mes y el que le va a quedar (Cuenta "Virtual" (setAside)) DONE
    Visualizador de logs DONE
    Borrado de operaciones demasiado antiguas
    Funcion Nuke (elimina todo y empieza de 0 la cuenta) DONE en Storage
        Balance por mes/año/semana DONE
    Grafico y stats con Pandas
    Evitar el reseteo tras ejecuciones (guardar los datos) DONE
    Acceder a tu cuenta con usuario y contraseña
    Menu y arbol de decisiones --> Archivo main Bajo la funcion iniciar()
    Crear func para importar el dataset a R y realizar analisis  #Primer objetivo sera hacer en R un grafico simple de los datos exportados de aqui
    Ordenar la tabla por fecha y por ID DONE
    Relacionar usuarios + contraseñas con operaciones
"""

class Gestor:
    def __init__(self, storage_filename="data.json"):
        # Iniciadores
        self.storage = Storage(storage_filename)
        self.logs = Logs(self.storage)

        # Atributos
        self.user_data = self.storage.data["users"]
        self.real_balance = 0.0
        self.virtual_balance = 0.0
        self.total_op = 0
        self.delta_balance = 0.0
        
        # Actualizar balance al inicializar
        self.actualizar_balance()

    def create_id(self, recursive: bool, concept: str, value: float):
        """Genera ID único, reutilizando para operaciones recursivas iguales"""
        if recursive:
            self.logs.reset_temp_log()
            self.logs.filter(Recursive=recursive, Concept=concept, Value=value)
            
            if self.logs.temp_log is None or self.logs.temp_log.empty:
                # Primera operación recursiva de este tipo
                return self.storage.get_next_id()
            else:
                # Reutilizar ID de operación recursiva existente
                return self.logs.temp_log.iloc[0]["ID"]
        else: 
            return self.storage.get_next_id()

    def get_operation_info(self):
        """Solicita información de operación al usuario con validación"""
        # FUNCIONES DE VALIDACIÓN
        def get_required_str(prompt):
            while True:
                value = input(prompt).strip()
                if value.lower() == "q":
                    print("Operación cancelada por el usuario.")
                    return None
                if value:
                    return value
                print("Este campo no puede estar vacío.")

        def get_positive_float(prompt):
            while True:
                value = input(prompt).strip()
                if value.lower() == "q":
                    print("Operación cancelada por el usuario.")
                    return None
                try:
                    value = float(value)
                    if value <= 0:
                        raise ValueError
                    return round(value, 2)
                except ValueError:
                    print("Introduce un número positivo válido.")

        def get_bool_from_symbol(prompt, true_symbol="+", false_symbol="-"):
            while True:
                value = input(prompt).strip()
                if value.lower() == "q":
                    print("Operación cancelada por el usuario.")
                    return None
                if value == true_symbol:
                    return True
                elif value == false_symbol:
                    return False
                else:
                    print(f"Introduce '{true_symbol}' o '{false_symbol}'.")

        def get_bool_from_01(prompt):
            while True:
                value = input(prompt).strip()
                if value.lower() == "q":
                    print("Operación cancelada por el usuario.")
                    return None
                if value in ("0", "1"):
                    return bool(int(value))
                print("Introduce 0 o 1.")

        def get_optional_str(prompt):
            value = input(prompt).strip()
            if value.lower() == "q":
                print("Operación cancelada por el usuario.")
                return False
            if value.lower() == "j" or value == "":
                return None
            return value

        def get_optional_date(prompt):
            while True:
                value = input(prompt).strip()
                if value.lower() == "q":
                    print("Operación cancelada por el usuario.")
                    return False
                if value.lower() == "j" or value == "":
                    return None
                try:
                    return datetime.datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    print("Formato inválido. Usa YYYY-MM-DD o 'j' para omitir.")

        # SOLICITAR INFORMACIÓN
        print("\tCAMPOS OBLIGATORIOS:\n")

        Concept = get_required_str("Escribe el concepto de la operación:\n")
        if Concept is None: return None

        Value = get_positive_float("Indica el importe de la operación:\n")
        if Value is None: return None

        IsIncome = get_bool_from_symbol("Presiona '+' si es ingreso, '-' si es gasto:\n")
        if IsIncome is None: return None

        Recursive = get_bool_from_01("¿La operación es recursiva? (1: Sí, 0: No):\n")
        if Recursive is None: return None

        # CAMPOS OPCIONALES
        print("\n\tCAMPOS OPCIONALES (pulsa 'j' para saltar):\n")

        To = get_optional_str("Nombre del destinatario:\n")
        if To is False: return None

        CreatedBy = get_optional_str("Nombre del remitente:\n")
        if CreatedBy is False: return None
       
        CreationDate = get_optional_date("Fecha de creación (YYYY-MM-DD):\n")
        if CreationDate is False: return None

        if not Recursive:
            EffectiveDate = get_optional_date("Fecha efectiva (YYYY-MM-DD):\n")
            if EffectiveDate is False: return None
        else:
            EffectiveDate = None

        ID = self.create_id(Recursive, Concept, Value)

        return {
            "ID": ID,
            "Concept": Concept,
            "Value": Value,
            "IsIncome": IsIncome,
            "Recursive": Recursive,
            "To": To,
            "CreatedBy": CreatedBy,
            "CreationDate": CreationDate,
            "EffectiveDate": EffectiveDate
        }

    def get_date(self, prompt):
        """Solicita una fecha al usuario con validación"""
        while True:
            value = input(prompt).strip()
            if value.lower() == "j":
                return None
            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                print("Formato inválido. Usa YYYY-MM-DD o 'j' para omitir.")

    def create_operation_from_data(self, data, effective_date=None):
        """Crea objeto Operation desde diccionario de datos"""
        return Operation(
            ID=data["ID"],
            Concept=data["Concept"],
            Value=data["Value"],
            IsIncome=data["IsIncome"],
            Recursive=data["Recursive"],
            To=data.get("To"),
            CreatedBy=data.get("CreatedBy"),
            CreationDate=effective_date or data.get("CreationDate"),
            EffectiveDate=effective_date or data.get("EffectiveDate")
        )

    def add_recursive_op(self, data):
        """Añade operaciones recursivas con intervalo especificado"""
        # Intervalo de repetición
        while True:
            try:
                interval_days = int(input("Cada cuántos días se repite la transacción: "))
                if interval_days <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Introduce un número entero positivo.")

        # Fechas de inicio y fin
        while True:
            start_date = data.get("EffectiveDate") or datetime.date.today()
            end_date = self.get_date("Fecha de finalización (YYYY-MM-DD o 'j' para indefinida): ")

            if end_date and start_date > end_date:
                print("La fecha de inicio es posterior a la fecha de finalización.")
                continue
            break

        i = 0
        current_date = start_date

        if end_date is None:
            # Sin fecha límite - máximo 60 operaciones
            while i < 60:
                op = self.create_operation_from_data(data, effective_date=current_date)
                self.logs.add_log(op)
                current_date += datetime.timedelta(days=interval_days)
                i += 1

            print(f"Se han creado {i} operaciones. Límite máximo alcanzado.")

        else:
            # Con fecha límite
            while current_date <= end_date:
                op = self.create_operation_from_data(data, effective_date=current_date)
                self.logs.add_log(op)
                current_date += datetime.timedelta(days=interval_days)
                i += 1
            print(f"Se han creado {i} operaciones recursivas.")

    def add_operation(self):
        """Interfaz principal para añadir operaciones"""
        data = self.get_operation_info()
        if data is None:
            print("Error en la creación de la operación.")
            return

        if data["Recursive"]:
            self.add_recursive_op(data)
            print("Operaciones recursivas creadas con éxito.")
        else:
            op = self.create_operation_from_data(data)
            self.logs.add_log(op)
            print("Operación creada con éxito.")
        
        # Actualizar balance tras añadir operaciones
        self.actualizar_balance()

    def find_true_balance(self, date=datetime.date.today()):
        """Calcula balance real hasta una fecha específica"""
        if not self.logs.data:
            return [0, 0.0]
        
        df = self.logs.get_dataframe()
        if df.empty:
            return [0, 0.0]
        
        # Filtrar por fecha efectiva
        df_filter = df[df["EffectiveDate"] <= pd.Timestamp(date)]
        
        if df_filter.empty:
            return [0, 0.0]
        
        total_op = len(df_filter)
        real_balance = df_filter["signed_value"].sum()
        
        return [total_op, real_balance]
 
    def actualizar_balance(self):
        """Actualiza todos los balances del gestor"""
        self.total_op, self.real_balance = self.find_true_balance()
        self.delta_balance = self.find_virtual_balance(manual=False)

    def get_deltatime(self, delta=None):
        """Obtiene fecha futura basada en delta de meses"""
        today = datetime.date.today()
        if delta is None:
            while True:
                delta_str = input(f"Indica el número de meses que quieres que pasen desde el {today}: ").strip()
                
                if delta_str == "":
                    delta = 1
                    break

                try:
                    delta = int(delta_str)
                    if delta > 0:
                        break
                    else:
                        print("Error: el número debe ser positivo.")
                except ValueError:
                    print("Error: indica un número entero positivo de meses, o no escribas nada.\n")

        end_date = today + relativedelta(months=delta)
        return end_date

    def find_virtual_balance(self, manual=True):
        """Calcula balance virtual/proyectado hacia el futuro"""
        if manual:
            end_date = self.get_deltatime()
        else:
            end_date = self.get_deltatime(delta=1)

        virtual_op, virtual_balance = self.find_true_balance(date=end_date)
        delta_balance = virtual_balance - self.real_balance

        if manual:  
            incoming_op = virtual_op - self.total_op
            print(f"Para el {end_date}, tu saldo será de {virtual_balance}€ y habrás realizado {incoming_op} operaciones nuevas!")
            print(f"Balance total en el periodo: {delta_balance}€.\n")
            
            # Actualizar virtual_balance cuando es consulta manual
            self.virtual_balance = virtual_balance
        else: 
            # Actualizar virtual_balance cuando es automático
            self.virtual_balance = virtual_balance

        return delta_balance

    def get_balance_by_period(self, period="month"):
        """Obtiene balance desglosado por períodos"""
        if not self.logs.data:
            print("No hay operaciones registradas")
            return {}
        
        df = self.logs.get_dataframe()
        if df.empty:
            return {}
        
        # Configurar agrupación según período
        if period == "month":
            df['period'] = df['EffectiveDate'].dt.to_period('M')
        elif period == "year":
            df['period'] = df['EffectiveDate'].dt.to_period('Y')
        elif period == "week":
            df['period'] = df['EffectiveDate'].dt.to_period('W')
        else:
            raise ValueError("Período debe ser 'month', 'year' o 'week'")
        
        # Agrupar y sumar
        balance_by_period = df.groupby('period')['signed_value'].sum().to_dict()
        
        print(f"\nBalance por {period}:")
        cumulative = 0
        for period_key, balance in balance_by_period.items():
            cumulative += balance
            print(f"{period_key}: {balance}€ (Acumulado: {cumulative}€)")
        
        return balance_by_period

    def export_to_csv(self, filename=None):
        """Exporta datos a CSV para análisis externo"""
        if not filename:
            filename = f"financial_export_{datetime.date.today().isoformat()}.csv"
        
        df = self.logs.get_dataframe()
        if df.empty:
            print("No hay datos para exportar")
            return False
        
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Datos exportados exitosamente a {filename}")
            return True
        except IOError as e:
            print(f"Error exportando datos: {e}")
            return False

    def get_statistics(self):
        """Genera estadísticas básicas del sistema"""
        if not self.logs.data:
            print("No hay operaciones para generar estadísticas")
            return
        
        df = self.logs.get_dataframe()
        if df.empty:
            return
        
        # Estadísticas básicas
        total_operations = len(df)
        income_ops = len(df[df['IsIncome'] == True])
        expense_ops = len(df[df['IsIncome'] == False])
        
        total_income = df[df['IsIncome'] == True]['Value'].sum()
        total_expenses = df[df['IsIncome'] == False]['Value'].sum()
        
        avg_income = df[df['IsIncome'] == True]['Value'].mean() if income_ops > 0 else 0
        avg_expense = df[df['IsIncome'] == False]['Value'].mean() if expense_ops > 0 else 0
        
        print(f"\n=== ESTADÍSTICAS FINANCIERAS ===")
        print(f"Total de operaciones: {total_operations}")
        print(f"Ingresos: {income_ops} operaciones, {total_income}€ total (promedio: {avg_income:.2f}€)")
        print(f"Gastos: {expense_ops} operaciones, {total_expenses}€ total (promedio: {avg_expense:.2f}€)")
        print(f"Balance actual: {self.real_balance}€")
        print(f"Balance proyectado (1 mes): {self.virtual_balance}€")
        print(f"Diferencia proyectada: {self.delta_balance}€")

    def nuke_data(self):
        """Elimina todos los datos del sistema tras confirmación"""
        confirmation = input("¿ESTÁS SEGURO de que quieres eliminar TODOS los datos? Esta acción no se puede deshacer.\nEscribe 'CONFIRMAR' para proceder: ")
        
        if confirmation == "CONFIRMAR":
            self.storage.nuke()
            # Reinicializar gestor
            self.logs = Logs(self.storage)
            self.user_data = self.storage.data["users"]
            self.real_balance = 0.0
            self.virtual_balance = 0.0
            self.total_op = 0
            self.delta_balance = 0.0
            print("Sistema reiniciado completamente.")
        else:
            print("Operación cancelada.")

    def view_logs(self, **kwargs):
        """Delegador para visualizar logs"""
        self.logs.view_logs(**kwargs)

    def filter_logs(self, **criteria):
        """Delegador para filtrar logs"""
        self.logs.filter(**criteria)

    def remove_operation(self, operation_id):
        """Delegador para eliminar operaciones"""
        self.logs.remove_log(operation_id)
        # Actualizar balance tras eliminación
        self.actualizar_balance()