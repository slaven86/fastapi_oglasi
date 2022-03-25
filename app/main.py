from fastapi import FastAPI
from . import auth, users, models, cars, admin, admin_cars
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
db = SessionLocal()



app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cars.router)
app.include_router(admin.router)
app.include_router(admin_cars.router)