from class_operation import Operation
import pandas as pd
import datetime

class Logs:
    def __init__(self):
        self.data = []
        self.temp_log = None #Para poder trabajar sobre logs una vez filtrado? 
    def add_log(self, operation: Operation):
        # Convertimos los campos indicados a un diccionario plano
        datalog = {
            "ID": operation.ID,
            "Concepto": operation.Concept,
            "Importe": operation.signed_value,
            "IsIncome": operation.IsIncome,
            "To": operation.To,
            "CreatedBy": operation.CreatedBy ,
            "Fecha_Creacion": operation.CreationDate,
            "Fecha_Ejecucion": operation.EffectiveDate
        }
        self.data.append(datalog)

    def get_log(self, OperationID: int):
        for log in self.data:
            if log["ID"] == OperationID:
                return log
        return None

    def remove_log(self, logID: int):
        log = self.get_log(logID)
        if log:
            self.data.remove(log)
            print(f"La operación '{log['ID']}: {log['Concepto']}' creada el {log['Fecha_Creacion']} ha sido eliminada")
        else:
            print("Error, no existe ninguna operación asociada a este ID")




    def view_logs(self, show_columns=None, reset=False):
        if reset:
            self.temp_log = None
        if not self.data:
            print("Todavía no se ha registrado ninguna operación")
            return
        
        if (self.temp_log is not None) and not (self.temp_log.empty):
            df = pd.DataFrame(self.temp_log)
        else:
            df = pd.DataFrame(self.data)

        base_columns = ["ID", "Concepto", "Fecha_Creacion", "Fecha_Ejecucion", "Importe"]

        # Añadir columnas adicionales manteniendo el orden y evitando duplicados

        if show_columns ==  "*": #Usando show_columns = "*" entonces generará el log completo
            showing_columns = base_columns + ["IsIncome", "To", "CreatedBy" ]
        elif show_columns:
            showing_columns = base_columns + [col for col in show_columns if col not in base_columns]
        else:
            showing_columns = base_columns #Caso base, no puede dar menos info 

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
        self.view_logs(show_columns= list(criteria.keys()), reset= False) #Ahora enseña los datos basicos de las operaciones filtradas + las columnas de criterios usadas. Para ampliar info, usar view_logs con reset = False


    def reset_temp_log(self):
        self.temp_log = None


    def add_recursive(self,interval:int, end:datetime ): #Interval tiene que darse en dias (Ej, cada semana = 7)
        recursive_operation = gestor.add_operation() #generar funcion en una clase gestor que cree operaciones  TO DO
        i = 0 #Contador para que no se generen mas de 365 operaciones
        while (recursive_operation.EffectiveDate <= end) and (i <= 365):
            self.add_log(recursive_operation)
            recursive_operation = gestor.add_operation()
            i += 1
        if i == 365:
            print("Se ha programado la operacion 365 veces. Maximo alcanzado \n")
        else:
            print(f"Se ha programado la operacion {i} veces \n")      

if __name__ == "__main__":

    logs = Logs()
    op1 = Operation(1,  "Pago Luz", 100.0, False, To="Endesa", CreatedBy="Usuario1")
    op2 = Operation(2,  "Sueldo", 1500.0, True, CreatedBy="EmpresaX")

    logs.add_log(op1)
    logs.add_log(op2)



    logs.filter(IsIncome = False )
    logs.view_logs(show_columns= "*")
    logs.view_logs(show_columns= None, reset= True) #El campo reset limpia el filtro sobre el que se ejecuta 
   



    #ToDo
    #def add_recursive (falta esto)
    #Falta pensar en como  crear la interfaz para que funcione con comandos sencillos
    


