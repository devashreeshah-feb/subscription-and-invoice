from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.user import User
from app.models.invoice import Invoice
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    subtotal: int
    tax: int
    total: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[InvoiceResponse])
def get_my_invoices(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).order_by(Invoice.created_at.desc()).all()
    return invoices
