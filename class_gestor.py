from class_operation import Operation
from class_logs import Logs
import datetime
import pandas

#Clase generadora de ID´s 
class IDGen:
    def __init__(self):
        self.n = 0  # estado interno

    def generarID(self):
        self.n += 1
        return self.n


Logs = Logs()
Generador = IDGen()


#TODO:
"""
    Crear una funcion que genere por inputs las operaciones
        Recursiva y normal (Ganancias y Perdidas)
    Guardar datos del usuario (Nombre, Dinero, Nº Operaciones (Entre x e y Fechas) )
    Tracker del dinero que lleva 
    Tracker del dinero que piensa gastar x mes y el que le va a quedar (Cuenta "Virtual" (setAside))
    Visualizador de logs
    Borrado de operaciones demasiado antiguas
    Funcion Nuke (elimina todo y empieza de 0 la cuenta)
    Balance por mes/año/semana
    Grafico y stats con Pandas
    Evitar el reseteo tras ejecuciones (guardar los datos)
    Acceder a tu cuenta con usuario y contraseña
    Menu y arbol de decisiones --> Archivo main Bajo la funcion iniciar()
    Crear func para importar el dataset a R y realizar analisis  #Primer objetivo sera hacer en R un grafico simple de los datos exportados de aqui
    Ordenar la tabla por fecha y por ID
"""

class Gestor:
    def __init__(self):
        self.user_data = []
        self.real_balance = None #float
        self.estimated_balance = None #float
    

    def create_id(self, recursive:bool, Concept:str, Value:float):
        if recursive:
            Logs.reset_temp_log()
            Logs.filter(Recursivo = recursive, Concepto = Concept, Importe = Value)
            if Logs.temp_log is None or Logs.temp_log.empty: #caso de que sea el primer elemento recursivo de una operacion
                 return Generador.generarID()
            else:
                return Logs.temp_log.iloc[0]["ID"]
        else: 
            return Generador.generarID()


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
                return None
            if value.lower() == "j" or value == "":
                return None
            return value

        def get_optional_date(prompt):
            while True:
                value = input(prompt).strip()
                if value.lower() == "q":
                    print("Operación cancelada por el usuario.")
                    return None
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
        if To is None and To != "": return None

        CreatedBy = get_optional_str("Nombre de quien lo recibe:\n")
        if CreatedBy is None and CreatedBy != "": return None

        CreationDate = get_optional_date("Fecha de creación (YYYY-MM-DD):\n")
        if CreationDate is None and CreationDate != "": return None

        EffectiveDate = get_optional_date("Fecha efectiva (YYYY-MM-DD):\n")
        if EffectiveDate is None and EffectiveDate != "": return None

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


