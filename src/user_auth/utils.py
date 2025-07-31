from datetime import datetime, timedelta, timezone
from typing import Annotated
from passlib.context import CryptContext
import secrets
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.config import get_session
from sqlalchemy.future import select
from src.school.models import User

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

db_dependency = Annotated[AsyncSession, Depends(get_session)]

def get_hashed_password(password):
    pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")
    hashed_pwd = pwd_context.hash(password)
    return hashed_pwd

def verify_password(password, hashed_password):
    pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")
    result = pwd_context.verify(password,hashed_password)
    return result

def generate_token(email, token_type):
    if token_type == "access_token":
        expiry = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    elif token_type == "refresh_token":
        expiry = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
    else:
        raise ValueError("Incorrect token_type")
    jwt_data = {"sub":email}
    jwt_data.update({"exp":expiry})
    encoded_jwt = jwt.encode(jwt_data, SECRET_KEY, ALGORITHM)
    return encoded_jwt

async def decode_token(token: str, db: db_dependency):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_email = decoded_token['sub']
        query = select(User).where(User.email==user_email)
        obj = await db.execute(query)
        user = obj.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not found")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Some error occured")
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency):
    user = await decode_token(token, db)
    return user


def required_role(role: str):
    def checker(user: User = Depends(get_current_user)):
        print(user)
        if user.role == role:
            return user
        return HTTPException(401)
    return checker