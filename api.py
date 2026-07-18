#para ejecutar el servidor: python3 -m uvicorn api:app --reload
#ejecuta en http://127.0.0.1:8000/

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

from class_gestor import Gestor
from parseo import OperationCreate, OperationOut, BalanceOut, ProjectionOut, CreateResult

app = FastAPI(title="Gestor Financiero API")

# Permite que prototipo.html (servido desde otro origen/puerto, o abierto
# como archivo local) pueda hacer fetch() a esta API sin que el navegador
# lo bloquee por CORS. En local esto es seguro; si algún día lo despliegas
# fuera de tu máquina, esto habría que restringirlo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gestor único, cargado al arrancar el servidor ---
gestor = Gestor()
gestor.storage.load()


def get_gestor() -> Gestor:
    """Dependencia: cada endpoint la pide como parámetro y recibe
    siempre la misma instancia (mismo patrón que 'iniciar()' en main.py,
    pero viviendo mientras el servidor esté encendido, no solo mientras
    dura una ejecución del script)."""
    return gestor

@app.get("/api/operations", response_model=List[OperationOut])
def list_operations(
    concepto: Optional[str] = None,
    importe: Optional[float] = None,
    ingreso: Optional[bool] = None,
    recursivo: Optional[bool] = None,
    destinatario: Optional[str] = None,
    usuario: Optional[str] = None,
    gestor: Gestor = Depends(get_gestor),
):
    criteria = {}
    if concepto is not None:
        criteria["Concepto"] = concepto
    if importe is not None:
        criteria["Importe"] = importe
    if ingreso is not None:
        criteria["IsIncome"] = ingreso
    if recursivo is not None:
        criteria["Recursivo"] = recursivo
    if destinatario is not None:
        criteria["Destinatario"] = destinatario
    if usuario is not None:
        criteria["Usuario"] = usuario

    if criteria:
        return gestor.storage.filter_operations(**criteria)
    return gestor.storage.list_operations()

@app.post("/api/operations", response_model=CreateResult)
def create_operation(payload: OperationCreate, gestor: Gestor = Depends(get_gestor)):
    data = payload.model_dump(exclude={"interval_days", "end_date"})
    if payload.Recursive:
        data["interval_days"] = payload.interval_days
        data["end_date"] = payload.end_date

    try:
        result = gestor.create_operation(data)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    gestor.storage.save()
    return result

@app.get("/api/balance", response_model=BalanceOut)
def get_balance(gestor: Gestor = Depends(get_gestor)):
    total_op, balance = gestor.find_true_balance()
    return BalanceOut(total_operations=total_op, balance=balance)

@app.get("/api/balance/projection", response_model=ProjectionOut)
def get_projection(months: int = 1, gestor: Gestor = Depends(get_gestor)):
    if months <= 0:
        raise HTTPException(status_code=400, detail="'months' debe ser positivo")
    return gestor.project_balance(months)

@app.delete("/api/operations/{op_id}")
def delete_operation(
    op_id: int,
    mode: str = "single",  # "single" = solo esta fecha, "family" = toda la serie
    creation_date: Optional[str] = None,  # requerido si mode="single" y es recursiva
    gestor: Gestor = Depends(get_gestor),
):
    log = gestor.storage.get_log(op_id)
    if log is None:
        raise HTTPException(status_code=404, detail=f"No existe operación con ID {op_id}")

    if not log["Recursive"]:
        gestor.storage.remove_operation(op_id)
        gestor.storage.save()
        return {"deleted": 1}

    if mode == "family":
        count = gestor.storage.remove_operation_family(op_id)
    else:
        if creation_date is None:
            raise HTTPException(
                status_code=400,
                detail="Operación recursiva: especifica 'creation_date' o usa mode='family'",
            )
        found = gestor.storage.remove_operation(op_id, creation_date)
        count = 1 if found else 0
        if count == 0:
            raise HTTPException(status_code=404, detail="No se encontró esa fecha concreta")

    gestor.storage.save()
    return {"deleted": count}