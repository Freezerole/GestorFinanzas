# schemas.py
from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import Optional

#Esquema de operaciones nuevas / crear operacion
class OperationCreate(BaseModel):
    Concept: str
    Value: float
    IsIncome: bool
    Recursive: bool
    To: Optional[str] = None
    CreatedBy: Optional[str] = None
    CreationDate: Optional[date] = None
    EffectiveDate: Optional[date] = None

    # Solo obligatorios si Recursive = True
    interval_days: Optional[int] = None
    end_date: Optional[date] = None

    @field_validator("Value")
    @classmethod
    def value_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("El importe debe ser positivo")
        return round(v, 2)

    @field_validator("Concept")
    @classmethod
    def concept_not_empty(cls, v):
        if not v.strip():
            raise ValueError("El concepto no puede estar vacío")
        return v

    @model_validator(mode="after")
    def check_recursive_fields(self):
        if self.Recursive and self.interval_days is None:
            raise ValueError("Una operación recursiva necesita 'interval_days'")
        if self.interval_days is not None and self.interval_days <= 0:
            raise ValueError("'interval_days' debe ser un entero positivo")
        return self

# Esquema de operaciones existentes / salida
class OperationOut(BaseModel):
    ID: int
    Concept: str
    Value: float
    IsIncome: bool
    Recursive: bool
    To: Optional[str] = None
    CreatedBy: Optional[str] = None
    CreationDate: date
    EffectiveDate: date

# Esquema del balance final
class BalanceOut(BaseModel):
    total_operations: int
    balance: float

# Esquema de proyección de balance
class ProjectionOut(BaseModel):
    end_date: date
    current_balance: float
    projected_balance: float
    delta: float
    new_operations: int

# Esquema de resultado de creación
class CreateResult(BaseModel):
    recursive: bool
    created: int
    ID: Optional[int] = None