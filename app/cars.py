from fastapi import APIRouter, status, HTTPException, Depends
from .schemas import CarCreate, UserOut, CarList, RateCar, RateCarCreate
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


#SORT BY BRAND
@router.get('/cars/brand', status_code=status.HTTP_200_OK, response_model=List[CarList])
def get_all_cars():
    all_cars = db.query(models.Car).order_by(models.Car.brand).all()
    return all_cars


#SORT BY MODEL
@router.get('/cars/model', status_code=status.HTTP_200_OK, response_model=List[CarList])
def get_all_cars():
    all_cars = db.query(models.Car).order_by(models.Car.model).all()
    return all_cars



#SORT BY YEAR
@router.get('/cars/year', status_code=status.HTTP_200_OK, response_model=List[CarList])
def get_all_cars():
    all_cars = db.query(models.Car).order_by(models.Car.year).all()
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
def add_car_rate(rating: RateCarCreate, current_user: UserOut = Depends(get_current_user)):
    if rating.rate not in range(1, 6):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Rate must be 1-5, try again")
    new_rate = models.RatingCar(car_id=rating.car_id, rate=rating.rate, owner_id=current_user.id)
    query = db.query(models.Car).filter(models.Car.owner_id == current_user.id,
                                           models.Car.id == rating.car_id).first()
    if query:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Can not rate your own car!")
    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)
    return {"msg": "Your rate added successfully"}




@router.get('/cars/rate/avg', status_code=status.HTTP_200_OK, response_model=List[RateCarCreate])
def get_all_avg_rate(current_user: UserOut = Depends(get_current_user)):

    avg = db.query(models.RatingCar.car_id, func.avg(models.RatingCar.rate)).group_by(models.RatingCar.car_id).order_by(func.avg(models.RatingCar.rate)).all()
    RateCarCreate = []
    for m in avg:
        car_id = m[0]
        rate = m[1]

        RateCarCreate.append(models.RatingCar(car_id=car_id, rate=rate))
    return RateCarCreate

