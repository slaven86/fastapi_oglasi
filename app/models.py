from .database import Base
from sqlalchemy import Column, Text, String, Integer, ForeignKey, Float, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    genre = Column(String(10))
    date_birth = Column(Date)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    username = Column(String(50))
    password = Column(String(200))
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))

    my_cars = relationship("Car", back_populates="owner")
    role = relationship("Role", back_populates="all_users")
    cars = relationship("Car", secondary="rating", back_populates="owners")



class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    description = Column(Text, nullable=False)
    brand = Column(String(20), nullable=False)
    model = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner = relationship("User", back_populates="my_cars")
    owners = relationship("User", secondary="rating", back_populates="cars")


class Rating(Base):
    __tablename__ = "rating"

    car_id = Column(Integer, ForeignKey('cars.id', ondelete="CASCADE"), primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    rate = Column(Float)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

    all_users = relationship("User", back_populates="role")


