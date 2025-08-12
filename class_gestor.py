from class_operation import Operation
from class_logs import Logs
import datetime
from dateutil.relativedelta import relativedelta  
import pandas as pd

#Clase generadora de ID´s 
class IDGen:
    def __init__(self):
        self.n = 0  # estado interno

    def generarID(self):
        self.n += 1
        return self.n


#TODO: #A partir de la base de datos generar um df completo con el que poder exportar datos csv y trabajar.  MOdo de persistencia csv
       #Es necesario guardar datos sobre las operaciones, el ultimo ID usado y a poder ser una base de usuario-contraseña. Ordenar df por fecha e ID 
#TODO:
"""
        Crear una funcion que genere por inputs las operaciones DONE
        Recursiva y normal (Ganancias y Perdidas) DONE
    Guardar datos del usuario (Nombre, Dinero, Nº Operaciones (Entre x e y Fechas) )
        Tracker del dinero que lleva DONE 
        Tracker del dinero que piensa gastar x mes y el que le va a quedar (Cuenta "Virtual" (setAside)) DONE
    Visualizador de logs
    Borrado de operaciones demasiado antiguas #PROBLEMA CON LA FORMA DE CALCULAR EL BALANCE
    Funcion Nuke (elimina todo y empieza de 0 la cuenta)
        Balance por mes/año/semana DONE
    Grafico y stats con Pandas
    Evitar el reseteo tras ejecuciones (guardar los datos) 
    Acceder a tu cuenta con usuario y contraseña
    Menu y arbol de decisiones --> Archivo main Bajo la funcion iniciar()
    Crear func para importar el dataset a R y realizar analisis  #Primer objetivo sera hacer en R un grafico simple de los datos exportados de aqui
    Ordenar la tabla por fecha y por ID
"""

class Gestor:
    def __init__(self):
        #iniciadores:
        self.logs = Logs()
        self.generador = IDGen()

        #atributos:
        self.user_data = []
        self.real_balance = 0.0 #float
        self.virtual_balance = 0.0 #float
        self.total_op = 0 # int
        self.delta_balance = 0.0 #float

    def create_id(self, recursive:bool, Concept:str, Value:float):
        if recursive:
            self.logs.reset_temp_log()
            self.logs.filter(Recursivo = recursive, Concepto = Concept, Importe = Value)
            if self.logs.temp_log is None or self.logs.temp_log.empty: #caso de que sea el primer elemento recursivo de una operacion
                 return self.generador.generarID()
            else:
                return self.logs.temp_log.iloc[0]["ID"]
        else: 
            return self.generador.generarID()


    def get_operation_info(self):
        # SETUP VALIDACIÓN Y SALIDA
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
                    return False #Se usa false para separar del None
                if value.lower() == "j" or value == "":
                    return None
                try:
                    return datetime.datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    print("Formato inválido. Usa YYYY-MM-DD o 'j' para omitir.")

        # EJECUCIÓN
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

        To = get_optional_str("Nombre de quien lo envía:\n")
        if To is False : return None

        CreatedBy = get_optional_str("Nombre de quien lo recibe:\n")
        if CreatedBy is False: return None
       
        CreationDate = get_optional_date("Fecha de creación (YYYY-MM-DD):\n")
        if CreationDate is False: return None
##

        if Recursive == False:
            EffectiveDate = get_optional_date("Fecha efectiva (YYYY-MM-DD):\n")
            if EffectiveDate is False: return None

        else:
            EffectiveDate = None
##

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
        while True:
            value = input(prompt).strip()
            if value.lower() == "j":
                return None
            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                print("Formato inválido. Usa YYYY-MM-DD o 'j' para omitir.")


    def create_operation_from_data(self, data, effective_date=None):
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

        # Intervalo de repetición
        while True:
            try:
                interval_days = int(input("Cada cuántos días se repite la transacción: "))
                if interval_days <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Introduce un número entero positivo.")

        while True:
                start_date = data.get("EffectiveDate") or datetime.date.today()
                end_date =self.get_date("Fecha de finalización (YYYY-MM-DD o 'j' para indefinida): ")

                if end_date and start_date > end_date:
                    print("La fecha de inicio es posterior a la fecha de finalización.")
                    continue
                break

        i = 0
        current_date = start_date

        if end_date is None:
            while i < 60:
                op = self.create_operation_from_data(data, effective_date=current_date)
                self.logs.add_log(op)
                current_date += datetime.timedelta(days=interval_days)
                i += 1

            print(f"Se han creado {i} operaciones. Límite máximo alcanzado.")

        else:
            while current_date <= end_date:
                op = self.create_operation_from_data(data, effective_date=current_date)
                self.logs.add_log(op)
                current_date += datetime.timedelta(days=interval_days)
                i += 1
            print(f"Se han creado {i} operaciones recursivas.")



    def add_operation(self):
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


    def find_true_balance(self, date = datetime.date.today()): #esta fecha viene dada en teoria por una entrada de log, para ver el balance al momento de hacer un pedido # si se borran entradas anteriores, como mantener eso
        df = pd.DataFrame(self.logs.data) #dataframe
        df_filter = df[df["Fecha_Ejecucion"] <= pd.Timestamp(date)]

        if df_filter.empty:
            total_op = 0
            real_balance = 0.0
        else:
            total_op = len(df_filter)
            real_balance = df_filter["Importe"].sum()

        return [total_op, real_balance]
        
 
    def actualizar_balance(self):
        self.total_op, self.real_balance = self.find_true_balance()
        self.delta_balance = self.find_virtual_balance(manual= False) #Actualiza de forma automatica el virtual a un mes de plazo sin pedir imputs. Añade una cuenta de el balance estimado a final de mes



    def get_deltatime(self, delta = None):
        today = datetime.date.today()
        if delta == None:
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

    


    def find_virtual_balance(self, manual = True): #fecha en la que dejas de estimar (para evitar problemas con recursivos) sea de un mes respecto a la fecha actual 
        if manual:
            end_date = self.get_deltatime()
        else:
            end_date = self.get_deltatime(delta=1)

        virtual_op, virtual_balance = self.find_true_balance(date = end_date)
        
        delta_balance = virtual_balance - self.real_balance

        if manual:  
            incoming_op = virtual_op - self.total_op
            print(f"Para el {end_date}, tu saldo será de {virtual_balance}€ y habrás realizado {incoming_op} operaciones nuevas!")
            print(f"Balance total en el periodo: {delta_balance}€. \n")

        else: 
            self.virtual_balance = virtual_balance #actualizar balance

        return delta_balance