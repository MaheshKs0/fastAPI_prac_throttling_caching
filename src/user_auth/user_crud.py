from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.school.models import User
from .utils import get_hashed_password, verify_password, generate_token
from .user_pydantic_models import CreateUser, UserLogin
from sqlalchemy.future import select

class UserCRUD:

    async def create_user(self, db: AsyncSession, data: CreateUser):
        user_data = data.model_dump()
        password = user_data.get('password')
        hashed_password = get_hashed_password(password)
        user_data['password'] = hashed_password
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_user_by_email(self,db: AsyncSession, email: str):
        query = select(User).where(User.email==email)
        user_obj = await db.execute(query)
        obj = user_obj.scalars().first()
        if obj:
            return obj
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user found with the email: {email}")

    async def login(self, db: AsyncSession, data: UserLogin):
        login_details = data.model_dump()
        password = login_details.get('password')
        email = login_details.get('email')
        user_obj = await self.get_user_by_email(db, email)
        hashed_password = user_obj.password
        if verify_password(password,hashed_password):
            atoken = generate_token(email, "access_token")
            rtoken = generate_token(email, "refresh_token")
        return {"access_token":atoken, "refresh_token":rtoken}

