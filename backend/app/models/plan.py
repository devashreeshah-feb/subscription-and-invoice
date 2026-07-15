import uuid
from sqlalchemy import Column, String, Integer, Boolean
from app.db.base_class import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Integer, nullable=False) # Store in cents
    billing_cycle = Column(String, default="monthly") # e.g. 'monthly', 'yearly'
    description = Column(String)
    active = Column(Boolean, default=True)
