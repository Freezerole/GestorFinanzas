#para ejecutar el servidor: python3 -m uvicorn api:app --reload
#ejecuta en http://127.0.0.1:8000/

from fastapi import FastAPI
app = FastAPI(title = "API Gestor Financiero",
            description = "API que permite planificar presupuestos y visualizarlos a lo largo de los meses.")

@app.get("/api/ping")
def ping():
    return {"status": "alive"}
