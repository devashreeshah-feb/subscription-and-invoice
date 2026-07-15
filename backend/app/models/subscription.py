import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String, ForeignKey("plans.id"), nullable=False)
    
    status = Column(String, default="Trial") # Trial, Active, Past Due, Cancelled, Expired
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True))
    
    user = relationship("User", backref="subscriptions")
    plan = relationship("Plan")
