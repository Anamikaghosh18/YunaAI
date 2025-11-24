from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # <-- changed
    auth_provider = Column(String(50), default="local")    # local or google
    google_id = Column(String(200), nullable=True)         # optional
    created_at = Column(DateTime, default=datetime.utcnow)
