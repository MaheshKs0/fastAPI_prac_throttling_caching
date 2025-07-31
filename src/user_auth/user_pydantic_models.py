from pydantic import BaseModel
from enum import Enum


class RoleEnum(str, Enum):
    teacher = "teacher"
    student = "student"


class CreateUser(BaseModel):
    username: str
    email: str
    role: RoleEnum
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


#Response Models

class CreateUserResponse(BaseModel):
    username: str
    email: str
    role: RoleEnum
