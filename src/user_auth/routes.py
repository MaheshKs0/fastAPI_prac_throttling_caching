from os import path
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.db.config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from .user_crud import UserCRUD
from .user_pydantic_models import CreateUser, CreateUserResponse, UserLogin

user_router = APIRouter(prefix="/users")

db_dependency = Annotated[AsyncSession,Depends(get_session)]

user_crud_class = UserCRUD()


@user_router.post("/register_user/", status_code=status.HTTP_201_CREATED, response_model=CreateUserResponse)
async def create_user(db: db_dependency, request_data: CreateUser):
    result = await user_crud_class.create_user(db, request_data)
    return result

@user_router.post("/user_login/", status_code=status.HTTP_200_OK)
async def login_user(db: db_dependency, request_data: UserLogin):
    result = await user_crud_class.login(db, request_data)
    return result