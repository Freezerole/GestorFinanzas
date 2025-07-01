# Gestor de Finanzas:
# Permite ver a futuro el balance real y "previsto" de una cuenta y acceder a un log con las operaciones futuras
# Permite también apartar importes a futuros basándose en gastos o ingresos previstos

import datetime

class Operation:
    def __init__(self, EffectiveDate: datetime.date, Concept: str, Value: float, IsIncome : bool, To=None, CreatedBy=None, CreationDate=None):


        self.EffectiveDate = EffectiveDate
        self.To = To
        self.Concept = Concept
        self.Value = Value
        self.CreatedBy = CreatedBy
        self.IsIncome = IsIncome


        if CreationDate is None:
            self.CreationDate = datetime.date.today()
        else:
            if CreationDate < EffectiveDate:
                self.CreationDate = CreationDate
            else:
                raise ValueError("La fecha de creacion no puede ser posterior a la fecha de oficialización de la transacción")



    # Propiedades:
    @property
    def EffectiveDate(self):
        return self._EffectiveDate

    @EffectiveDate.setter
    def EffectiveDate(self, value):
        if isinstance(value, datetime.date) and datetime.date.today() <= value:
            self._EffectiveDate = value
        else:
            raise ValueError("No puedes programar una operación para un día ya pasado")
        

    @property
    def Concept(self):
        return self._Concept

    @Concept.setter
    def Concept(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._Concept = value
        else:
            raise TypeError("El concepto tiene que ser una palabra o frase")
        

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, value):
        if isinstance(value, (float, int)) and value > 0:
            self._Value = round(value, 2)
        else:
            raise ValueError("La cantidad tiene que ser positiva")
    
    @property
    def IsIncome(self):
        return self._IsIncome
    
    @IsIncome.setter
    def IsIncome(self, value):
        if isinstance(value, bool):
            self.IsIncome = value
        else:
            raise TypeError("Este campo solo acepta booleanos")

    @property
    def To(self):
        return self._To

    @To.setter
    def To(self, value):
        if (isinstance(value, str) and len(value) > 0) or (value is None):
            self._To = value
        else:
            raise TypeError("El destinatario tiene que ser un nombre o None")
        

    @property       
    def CreatedBy(self):
        return self._CreatedBy

    @CreatedBy.setter
    def CreatedBy(self, value):
        if (isinstance(value, str) and len(value) > 0) or (value is None):
            self._CreatedBy = value
        else:
            raise TypeError("El CreatedBy tiene que ser un nombre (str) o None")



    def __str__(self):
        parts = [
            f"CreatedBy: {self.CreatedBy}",
            f"Concept: {self.Concept}",
            f"Value: {self.Value}€",
            f"CreationDate: {self.CreationDate}",
            f"EffectiveDate: {self.EffectiveDate.strftime('%d - %m - %Y')}"
            
        ]

        if self.To:
            parts.append(f"To: {self.To}")

        if self.CreatedBy:
            parts.append(f"CreatedBy: {self.CreatedBy}")

        return ", ".join(parts)


