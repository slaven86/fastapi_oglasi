from fastapi import APIRouter, status, HTTPException, Depends
from .database import SessionLocal
from .schemas import UserCreate, UserOut, RoleCreate, CarList
from . import models
import validators
from passlib.hash import pbkdf2_sha256
from typing import List
from .token import get_current_user




router = APIRouter(tags=['Users'])
db = SessionLocal()



@router.post('/role', status_code=status.HTTP_201_CREATED)
def add_role(role: RoleCreate):
    new_role = models.Role(name=role.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return {"msg": "New role created!"}




@router.post('/users', status_code=status.HTTP_201_CREATED)
def add_user(user: UserCreate):
    if len(user.first_name) < 2:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="First name must be min 2 characters!")

    if not user.first_name.isalpha():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="First name must be only letters!")

    if len(user.last_name) < 2:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Last name must be min 2 characters!")

    if not user.last_name.isalpha() or " " in user.last_name:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Last name must be only letters!")



    if not validators.email(user.email):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Not valid email!")

    if db.query(models.User).filter(models.User.email == user.email).first() is not None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email already exist!")

    if not user.username.isalnum() or " " in user.username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Username must be alphanumeric, also no spaces!")
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username already exist!")

    if len(user.password) < 6:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Password must be min 6 characters!")


    hashed_pass = pbkdf2_sha256.hash(user.password)
    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        genre=user.genre,
        email=user.email,
        username=user.username,
        password=hashed_pass,
        role_id=1)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "New user created!"}




@router.get('/users', response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_all_users():
    all_users = db.query(models.User).all()
    return all_users


@router.get('/users/{id}', status_code=status.HTTP_200_OK, response_model=UserOut)
def get_single_recipe(id: int, current_user: UserOut = Depends(get_current_user)):
    single_user = db.query(models.User).filter(models.User.id == id, models.User.id == current_user.id).first()


    if single_user:
        return single_user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist!")


@router.put('/users/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_user(id:int, user: UserCreate, current_user: UserOut = Depends(get_current_user)):

    user_update = db.query(models.User).filter(
        models.User.id == current_user.id, models.User.id == id).first()

    if not user_update:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only owner can update this page!")

    hashed_pass = pbkdf2_sha256.hash(user.password)
    user_update.first_name = user.first_name
    user_update.last_name = user.last_name
    user_update.genre = user.genre
    user_update.email = user.email
    user_update.username = user.username
    user_update.password = hashed_pass
    db.commit()
    return {"msg": "User is updated!"}


@router.delete('/users/{id}', status_code=status.HTTP_200_OK)
def delete_user(id:int, current_user: UserOut = Depends(get_current_user)):
    user_delete = db.query(models.User).filter(
        models.User.id == current_user.id, models.User.id == id).first()

    if not user_delete:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only owner can delete this page!")

    db.delete(user_delete)
    db.commit()
    return {"msg": "Recipe has been deleted!"}



@router.get('/users/{id}/cars', status_code=status.HTTP_200_OK, response_model=List[CarList])
def get_own_cars(id: int, current_user: UserOut = Depends(get_current_user)):
    single_user = db.query(models.User).get(id)
    all_my_cars = single_user.my_cars
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if single_user == user:
        return all_my_cars
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only owner can see this page!")


