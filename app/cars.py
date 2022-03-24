from fastapi import APIRouter, status, HTTPException, Depends
from .schemas import CarCreate, UserOut, CarList, Rate, RateCreate
from .token import get_current_user
from . import models
from .database import SessionLocal
from typing import List
from sqlalchemy.sql import func, desc


router = APIRouter(tags=['Cars'])
db = SessionLocal()

@router.post('/cars', status_code=status.HTTP_201_CREATED)
def add_car(car: CarCreate, current_user: UserOut = Depends(get_current_user)):

    new_car = models.Car(name=car.name,
                         description=car.description,
                         brand=car.brand,
                         model=car.model,
                         year=car.year,
                         owner_id=current_user.id
                         )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return {"msg": "New car created!"}



@router.get('/cars', status_code=status.HTTP_200_OK, response_model=List[CarList])
def get_all_cars():
    all_cars = db.query(models.Car).all()
    return all_cars



@router.get('/cars/{id}', status_code=status.HTTP_200_OK, response_model=CarList)
def get_single_car(id: int):
    single_car = db.query(models.Car).filter(models.Car.id == id).first()
    if not single_car:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Car does not exist!")
    return single_car




@router.put('/cars/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_car(id:int, car: CarCreate, current_user: UserOut = Depends(get_current_user)):

    car_update = db.query(models.Car).filter(
        models.Car.owner_id == current_user.id, models.Car.id == id).first()

    if not car_update:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only owner can update this page!")

    car_update.name = car.name
    car_update.description = car.description
    car_update.brand = car.brand
    car_update.model = car.model
    car_update.year = car.year
    db.commit()
    return {"msg": "Car is updated!"}



@router.delete('/cars/{id}', status_code=status.HTTP_200_OK)
def delete_car(id:int, current_user: UserOut = Depends(get_current_user)):
    car_delete = db.query(models.Car).filter(
        models.Car.owner_id == current_user.id, models.Car.id == id).first()

    if not car_delete:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only owner can delete this page!")

    db.delete(car_delete)
    db.commit()
    return {"msg": "Car has been deleted!"}


@router.post('/cars/rate', status_code=status.HTTP_201_CREATED)
def add_car_rate(rating: RateCreate, current_user: UserOut = Depends(get_current_user)):
    if rating.rate not in range(1, 6):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Rate must be 1-5, try again")
    new_rate = models.Rating(car_id=rating.car_id, rate=rating.rate, owner_id=current_user.id)
    query = db.query(models.Car).filter(models.Car.owner_id == current_user.id,
                                           models.Car.id == rating.car_id).first()
    if query:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Can not rate your own car!")
    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)
    return {"msg": "Your rate added successfully"}



@router.get('/cars/{id}/rate', status_code=status.HTTP_200_OK,response_model=Rate)
def get_avg_car_rate(id: int, current_user: UserOut = Depends(get_current_user)):
    single_car = db.query(models.Car).filter(models.Car.id == id,
                                                   models.Car.owner_id == current_user.id).first()

    if single_car:
        avg = db.query(func.avg(models.Rating.rate)).filter(models.Rating.car_id == id).first()
        return Rate(rate=avg[0])
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Car does not exist!")




