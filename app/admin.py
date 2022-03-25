from fastapi import APIRouter, status, HTTPException, Depends
from .database import SessionLocal
from .schemas import UserCreate, UserOut
from . import models
import validators
from passlib.hash import pbkdf2_sha256
from .token import get_current_user
from datetime import datetime




router = APIRouter(tags=['Admin'])
db = SessionLocal()



#ADD ADMIN USER
@router.post('/admin', status_code=status.HTTP_201_CREATED)
def admin_add_user(user: UserCreate, current_user: UserOut = Depends(get_current_user)):

    logged_in_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if logged_in_user.role_id != 2:
        return {"message": " You must be logged in as admin"}


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

    dob = datetime.strptime(str(user.date_birth), "%Y-%m-%d")
    date_birth = str(dob)[:10]



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
        date_birth=date_birth,
        role_id=2)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "New admin created!"}


# DELETE ANYONE USER
@router.delete('/admin/users/{id}', status_code=status.HTTP_200_OK)
def admin_delete_user(id:int, current_user: UserOut = Depends(get_current_user)):
    logged_in_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if logged_in_user.role_id != 2:
        return {"message": " You must be logged in as admin"}

    user_delete = db.query(models.User).filter(models.User.id == id).first()


    db.delete(user_delete)
    db.commit()
    return {"msg": "User has been deleted!"}



