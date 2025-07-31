from calendar import c
from operator import gt
from typing import Annotated, List
from anyio import Path
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from src.db.config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from .pydantic_models import CreateFeedBack, CreateSubject, GetTeachers, FeedbackWithSubject, UpdateFeedBack
from .fb_crud import FeedbackCRUD
from .models import User
from src.user_auth.utils import get_current_user, required_role
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter


#uvicorn src.main:app --reload

feedback_router = APIRouter(prefix="/feedback")

fb_crud_class = FeedbackCRUD()

db_dependency = Annotated[AsyncSession, Depends(get_session)]

@feedback_router.post("/create_feedback/", status_code=status.HTTP_201_CREATED)
async def create_feedback(db: db_dependency, request_data: CreateFeedBack, user: Annotated[User, Depends(required_role("teacher"))]):
    fb_data = request_data.model_dump()
    result = await fb_crud_class.create_feedback(db, fb_data, user)
    return Response(content=result)


@feedback_router.get("/get_all_teachers/", status_code=status.HTTP_200_OK, response_model=list[GetTeachers],dependencies=[Depends(RateLimiter(times=5,seconds=60,
                                                                                                                   identifier="user_identifier"))])
async def get_teachers(db: db_dependency, user: Annotated[User, Depends(required_role("teacher"))]):
    teacher_objects = await fb_crud_class.get_all_teachers(db)
    return teacher_objects


@feedback_router.get("/get_teacher/{teacher_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5,seconds=60))])
async def get_teacher(db: db_dependency, user: Annotated[User, Depends(required_role("teacher"))],teacher_id: int = Path(...,gt=0)):
    result = await fb_crud_class.get_teacher(db,teacher_id)
    if result == 'Not a valid id':
        raise HTTPException(content=result, status_code=status.HTTP_404_NOT_FOUND)
    return result


@feedback_router.post("/create_subject/", status_code=status.HTTP_201_CREATED)
async def create_subject(db: db_dependency,user: Annotated[User, Depends(required_role("teacher"))], request_data: CreateSubject):
    result = await fb_crud_class.create_subject(db, request_data)
    if result == "Not a valid userId":
        raise HTTPException(content=result, status_code=status.HTTP_404_NOT_FOUND)
    return Response(content=result)


@feedback_router.get("/get_feedback", status_code=status.HTTP_200_OK,response_model= list[FeedbackWithSubject],
                     dependencies=[Depends(RateLimiter(times=5,seconds=60))])
async def get_feedback(db: db_dependency, user: Annotated[User, Depends(required_role("student"))]):
    result = await fb_crud_class.get_teacher_feedback(db, user)
    if not result:
        raise HTTPException(content=result, status_code=status.HTTP_404_NOT_FOUND)
    return result


@feedback_router.put("/update_feedback/{feedback_id}", status_code=status.HTTP_200_OK)
async def update_feedback(db:db_dependency, user: Annotated[User, Depends(required_role("student"))],request_data: UpdateFeedBack,
                          feedback_id: int = Path(gt=0)):
    data = request_data.model_dump()
    result = await fb_crud_class.update_feedback(db, user, feedback_id, data)
    if result == "No Feeback found":
        raise HTTPException(content=result, status_code=status.HTTP_404_NOT_FOUND)
    return result
