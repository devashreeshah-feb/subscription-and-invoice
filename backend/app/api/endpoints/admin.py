from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.user import User
from app.models.subscription import Subscription
from app.models.payment import Payment

router = APIRouter()

def check_admin(current_user: User = Depends(deps.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(check_admin)
):
    total_customers = db.query(func.count(User.id)).filter(User.role == "customer").scalar()
    
    active_subscriptions = db.query(func.count(Subscription.id)).filter(Subscription.status == "Active").scalar()
    
    # Calculate MRR (sum of price of all active plans) - simplified
    from app.models.plan import Plan
    mrr_result = db.query(func.sum(Plan.price)).join(Subscription).filter(Subscription.status == "Active").scalar()
    mrr = (mrr_result or 0) / 100 # Convert to actual currency units
    
    failed_payments = db.query(func.count(Payment.id)).filter(Payment.status == "failed").scalar()
    
    return {
        "total_customers": total_customers,
        "active_subscriptions": active_subscriptions,
        "mrr": mrr,
        "failed_payments": failed_payments
    }
