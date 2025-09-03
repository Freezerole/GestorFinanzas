import datetime
from typing import Optional

class Operation:
    def __init__(self, ID: int, Concept: str, Value: float, IsIncome: bool, Recursive: bool,  To = None, CreatedBy = None, CreationDate = None, EffectiveDate = None):

        self.ID = ID
        self.Concept = Concept
        self.Value = Value
        self.IsIncome = IsIncome
        self.To = To
        self.Recursive = Recursive
        self.CreatedBy = CreatedBy

        self._CreationDate = CreationDate or datetime.date.today()

        if EffectiveDate is not None:
            if not isinstance(EffectiveDate, datetime.date):
                raise TypeError("EffectiveDate debe ser una instancia de datetime.date")
            if EffectiveDate < self._CreationDate:
                raise ValueError("EffectiveDate no puede ser anterior a CreationDate")
            self._EffectiveDate = EffectiveDate
        else:
            self._EffectiveDate = self._CreationDate

# Si la fecha de Creacion esta vacia, se asume hoy
# Si la fecha de Ejecucion eta vacia, se asume CreacionDate
# Es posible poner fechas a pasado mientras cumpla la restriccion del EjecutionDate

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value):
        if isinstance(value, int) and value > 0:
            self._ID = value
        else:
            raise ValueError("ID debe ser un entero positivo")

    @property
    def Concept(self):
        return self._Concept

    @Concept.setter
    def Concept(self, value):
        if isinstance(value, str) and value.strip():
            self._Concept = value
        else:
            raise TypeError("El concepto tiene que ser una palabra o frase no vacía")

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, value):
        if isinstance(value, (float, int)) and value > 0:
            self._Value = round(float(value), 2)
        else:
            raise ValueError("La cantidad tiene que ser positiva")

    @property
    def IsIncome(self):
        return self._IsIncome

    @IsIncome.setter
    def IsIncome(self, value):
        if isinstance(value, bool):
            self._IsIncome = value
        else:
            raise TypeError("Este campo solo acepta booleanos")
        
    @property
    def Recursive(self):
        return self._Recursive
    
    @Recursive.setter
    def Recursive(self,value):
        if isinstance(value, bool):
            self._Recursive = value
        else:
            raise TypeError("Este campo solo acepta booleanos")


    @property
    def To(self):
        return self._To

    @To.setter
    def To(self, value):
        if value is None or (isinstance(value, str) and value.strip()):
            self._To = value
        else:
            raise TypeError("El destinatario tiene que ser un nombre válido o None")

    @property
    def CreatedBy(self):
        return self._CreatedBy

    @CreatedBy.setter
    def CreatedBy(self, value):
        if value is None or (isinstance(value, str) and value.strip()):
            self._CreatedBy = value
        else:
            raise TypeError("CreatedBy debe ser un string válido o None")

    @property
    def CreationDate(self):
        return self._CreationDate

    @property
    def EffectiveDate(self):
        return self._EffectiveDate

    @property
    def signed_value(self):
        return self.Value if self.IsIncome else -self.Value

    def __str__(self):
        parts = [
            f"Operation ID: {self.ID}",
            f"CreatedBy: {self.CreatedBy}",
            f"Concept: {self.Concept}",
            f"Value: {self.Value}€",
            f"CreationDate: {self.CreationDate}",
            f"EffectiveDate: {self.EffectiveDate}"
        ]
        if self.To:
            parts.append(f"To: {self.To}")
        return ", ".join(parts)


    def to_dict(self): # 🔹 Convierte el objeto a un dict serializable
        return {
            "ID": self.ID,
            "Concept": self.Concept,
            "Value": self.Value,
            "IsIncome": self.IsIncome,
            "Recursive": self.Recursive,
            "To": self.To,
            "CreatedBy": self.CreatedBy,
            "CreationDate": self.CreationDate.isoformat() if self.CreationDate else None,
            "EffectiveDate": self.EffectiveDate.isoformat() if self.EffectiveDate else None,
        }

    
    @classmethod
    def from_dict(cls, data):# 🔹 Reconstruye un objeto Operation desde un dict (JSON cargado)
        return cls(
            ID=data["ID"],
            Concept=data["Concept"],
            Value=data["Value"],
            IsIncome=data["IsIncome"],
            Recursive=data.get("Recursive", False),
            To=data.get("To"),
            CreatedBy=data.get("CreatedBy"),
            CreationDate=datetime.date.fromisoformat(data["CreationDate"]) if data.get("CreationDate") else None,
            EffectiveDate=datetime.date.fromisoformat(data["EffectiveDate"]) if data.get("EffectiveDate") else None,
        )
    