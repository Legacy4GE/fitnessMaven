from fastapi import FastAPI

from app.api.auth import router as auth_router

app = FastAPI(
    title="fitnessMaven",
    description="Gym courtesy timer API",
    version="0.1.0",
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
