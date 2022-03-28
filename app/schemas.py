from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class RoleCreate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class GenreCreate(BaseModel):
    name: str

    class Config:
        orm_mode = True




class User(BaseModel):
    username: str

    class Config:
        orm_mode = True



class UserCreate(BaseModel):
    first_name: str
    last_name: str
    genre_id: int
    date_birth: Optional[date]
    email: str
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str
    username: str
    role: RoleCreate

    class Config:
        orm_mode = True


class CarCreate(BaseModel):
    name: str
    description: str
    brand: str
    model: str
    year: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class CarList(BaseModel):
    id: int
    name: str
    description: str
    brand: str
    model: str
    year: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_active: bool
    owner_id: int
    owner: User

    class Config:
        orm_mode = True


class RateCarCreate(BaseModel):
    car_id: int
    rate: float

    class Config:
        orm_mode = True



class RateCar(BaseModel):
    rate: float

    class Config:
        orm_mode = True




class TokenData(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None