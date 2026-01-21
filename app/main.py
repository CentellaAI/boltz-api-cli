from fastapi import FastAPI

from app.routers import predict,results
from app.routers import analysis

app = FastAPI(
    title="Boltz FastAPI + CLI",
    description="FastAPI service that orchestrates Boltz CLI inference",
    version="1.0.0",
)

app.include_router(predict.router)
app.include_router(analysis.router)
app.include_router(results.router)
@app.get("/health")
def health_check():
    return {"status": "ok"}
