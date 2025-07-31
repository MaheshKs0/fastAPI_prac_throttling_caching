from pydantic import BaseModel
from datetime import date


class CreateFeedBack(BaseModel):
    student_id: int
    feedback_text: str
    date: date
    subject_id: int


class CreateSubject(BaseModel):
    name: str
    teacher_id: int


#Response Models

class GetTeachers(BaseModel):
    id: int
    role: str
    username: str

class FeedbackWithSubject(BaseModel):
    id: int
    student_id: int
    subject_name: str
    feedback_text: str
    date: date

    class Config:
        orm_mode = True
