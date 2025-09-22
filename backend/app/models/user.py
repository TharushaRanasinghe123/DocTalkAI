from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.PATIENT
    phone: Optional[str] = None

class UserCreateByAdmin(UserBase):
    password: str
    specialization: str
    role: UserRole = UserRole.DOCTOR

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: str
    role: UserRole
    phone: Optional[str] = None

    class Config:
        from_attributes = True