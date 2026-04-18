from ..database.db import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime, timezone


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    score = Column(Integer)
    decision = Column(String(50))
    action = Column(String(50))
    response_text = Column(Text)
    raw_analysis = Column(JSON)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(255), unique=True, nullable=False,index=True)
    expires_at = Column(DateTime(timezone=True),nullable=False)
