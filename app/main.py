from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.pages import router as pages_router
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.auth.passwords import hash_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed test user on startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).filter(User.email == "test").first():
        db.add(User(email="test", hashed_password=hash_password("test"), full_name="Test User"))
        db.commit()
    db.close()
    yield


app = FastAPI(
    title="fitnessMaven",
    description="Gym courtesy timer API",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
