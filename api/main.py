from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import alertas, cientifico, radar, reconciliacao
import uvicorn


app = FastAPI(
    title="SENTINELA API",
    description="Backend API for the SENTINELA project connecting to NEAC database",
    version="1.0.0"
)

# Configure CORS for frontend communication
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",  # Default Vite port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alertas.router, prefix="/api/v1/alertas", tags=["Alertas"])
app.include_router(cientifico.router, prefix="/api/v1/cientifico", tags=["Científico"])
app.include_router(radar.router, prefix="/api/v1/radar", tags=["Radar CAD"])
app.include_router(reconciliacao.router, prefix="/api/v1/reconciliacao", tags=["Reconciliação"])


@app.get("/health", tags=["System"])
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
