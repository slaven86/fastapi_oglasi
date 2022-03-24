from fastapi import FastAPI
from . import auth, users, models, cars
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
db = SessionLocal()



app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cars.router)