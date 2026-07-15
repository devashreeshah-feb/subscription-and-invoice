import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    
    invoice_number = Column(String, unique=True, index=True)
    subtotal = Column(Integer, nullable=False) # In cents
    tax = Column(Integer, default=0) # In cents
    total = Column(Integer, nullable=False) # In cents
    
    status = Column(String, default="paid") # paid, open, void
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
    subscription = relationship("Subscription")
