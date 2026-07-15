import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    account_type = Column(String, default="individual") # "individual" or "organization"
    organization_name = Column(String, nullable=True)
    role = Column(String, default="customer") # "customer" or "admin"
