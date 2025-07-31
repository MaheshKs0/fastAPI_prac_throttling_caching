from ast import Sub
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Feedback, Subject, User

class FeedbackCRUD:

    async def create_feedback(self, db: AsyncSession, data: dict, user: User):
        sub_id = data.get('subject_id')
        subject_obj = await self.get_subject(db, sub_id)
        if not subject_obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="subject not found. please share the correct subject ID")
        teacher = subject_obj.teacher_id
        if user.id == teacher:
            fb_obj = Feedback(**data)
            db.add(fb_obj)
            await db.commit()
            await db.refresh(fb_obj)
            return "feedback has been added"
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't give feedback for a subject which you don't teach")


    async def get_subject(self, db: AsyncSession, id:int):
        query = select(Subject).where(Subject.id == id)
        obj = await db.execute(query)
        if obj:
            subj =obj.scalars().first()
            return subj
        return None

    async def get_user(self, db: AsyncSession, id: int):
        query = select(User).where(User.id == id)
        obj = await db.execute(query)
        if obj:
            user =obj.scalars().first()
            return user
        return None


    async def get_teacher(self, db: AsyncSession, id: int):
        query = select(User).where(User.id==id)
        obj = await db.execute(query)
        user = obj.scalars().first()
        if user and user.role == 'teacher':
            return user
        return "Not a valid id"


    async def create_subject(self, db: AsyncSession, data: dict):
        subj_data = data.model_dump()
        id = subj_data.get('teacher_id')
        user_obj = await self.get_user(db, id)
        if user_obj.role == "teacher":
            obj = Subject(**subj_data)
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return "subject has been created"
        return "Not a valid userId"


    async def get_all_teachers(self, db: AsyncSession):
        query = select(User)
        result =await db.execute(query)
        users = result.scalars().all()
        teachers = [user for user in users if user.role == "teacher"]
        return teachers
