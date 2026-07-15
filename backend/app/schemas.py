from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    account_type: str = "individual"
    organization_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    verified: bool
    account_type: str
    organization_name: Optional[str] = None
    role: str = "customer"
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PlanResponse(BaseModel):
    id: str
    name: str
    price: int
    billing_cycle: str
    description: Optional[str]
    active: bool

    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    plan_id: str
    payment_method_id: str

class SubscriptionResponse(BaseModel):
    id: str
    plan_id: str
    status: str
    starts_at: datetime
    next_billing_date: datetime
    
    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: str
    amount: int
    status: str
    transaction_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
