from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text

Base = declarative_base()

class User(Base):
    __tablename__ = "school_user"
    id = Column(Integer, unique=True, primary_key=True)
    username = Column(String)
    email = Column(String, unique=True)
    role  = Column(String)
    password = Column(String)


class Subject(Base):
    __tablename__ = "school_subject"

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String)
    teacher_id = Column(ForeignKey("school_user.id"))


class Feedback(Base):
    __tablename__ = "school_feedback"

    id = Column(Integer, unique=True, primary_key=True)
    student_id = Column(ForeignKey("school_user.id"))
    subject_id = Column(ForeignKey("school_subject.id"))
    feedback_text = Column(Text)
    date = Column(Date)

