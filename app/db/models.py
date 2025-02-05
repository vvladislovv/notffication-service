from sqlalchemy import Column, Integer, String, DateTime,TIMESTAMP,JSON
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    type_content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 


class LogsJson(Base):
    __tablename__ = "logs_json"
    
    id = Column(Integer, primary_key=True)
    data = Column(JSON)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now().replace(second=0, microsecond=0), nullable=False)
    