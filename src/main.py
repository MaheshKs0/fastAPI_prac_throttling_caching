from fastapi import FastAPI
from contextlib import asynccontextmanager

import redis
from src.db.config import init_db, init_redis
from src.school.routes import feedback_router
from src.user_auth.routes import user_router

@asynccontextmanager
async def life_span(app:FastAPI):
    """please check the explanation below and UNDERSTAND why we have this code here."""
    print(f"server is staring...")
    await init_db()
    await init_redis()
    yield
    """
    Before yield → Startup code runs (init_db(), logging, etc.).
    At yield → FastAPI takes over and starts handling requests.
    After yield → Shutdown cleanup runs (print(f"server has been stopped")).
    """
    print(f"server has been stopped")

version = "V1"
app = FastAPI(version=version,
              title="feedbacks",
              description="A REST API for teachers to create, update and delete feedback and for students to check the feedback",
              lifespan=life_span,

)

app.include_router(feedback_router)
app.include_router(user_router)