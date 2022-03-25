from fastapi import APIRouter, status, HTTPException, Depends
from .schemas import UserOut
from .token import get_current_user
from . import models
from .database import SessionLocal



router = APIRouter(tags=['Admin-Cars'])
db = SessionLocal()



@router.delete('/admin/cars/{id}', status_code=status.HTTP_200_OK)
def admin_delete_car(id:int, current_user: UserOut = Depends(get_current_user)):
    logged_in_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if logged_in_user.role_id != 2:
        return {"message": " You must be logged in as admin"}

    car_delete = db.query(models.Car).filter(models.Car.id == id).first()

    db.delete(car_delete)
    db.commit()
    return {"msg": "Car has been deleted!"}

