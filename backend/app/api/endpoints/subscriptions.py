from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List
from app.api import deps
from app.schemas import SubscriptionCreate, SubscriptionResponse, PaymentResponse
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.invoice import Invoice

router = APIRouter()

@router.post("/", response_model=SubscriptionResponse)
def create_subscription(
    sub_in: SubscriptionCreate, 
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    plan = db.query(Plan).filter(Plan.id == sub_in.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    active_sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "Active"
    ).first()
    
    if active_sub:
        raise HTTPException(status_code=400, detail="User already has an active subscription. Please use upgrade/downgrade.")

    now = datetime.now(timezone.utc)
    next_billing = now + timedelta(days=30) if plan.billing_cycle == 'monthly' else now + timedelta(days=365)

    subscription = Subscription(
        user_id=current_user.id,
        plan_id=plan.id,
        status="Active", 
        starts_at=now,
        next_billing_date=next_billing
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    if sub_in.payment_method_id == "pm_fail":
        payment_status = "failed"
        subscription.status = "Past Due"
    else:
        payment_status = "success"
        
    payment = Payment(
        subscription_id=subscription.id,
        amount=plan.price,
        status=payment_status,
        gateway="pseudo_stripe",
        transaction_id=f"txn_{subscription.id}_{now.timestamp()}"
    )
    db.add(payment)
    
    # Generate Invoice on Success
    if payment_status == "success":
        invoice = Invoice(
            user_id=current_user.id,
            subscription_id=subscription.id,
            invoice_number=f"INV-{now.strftime('%Y%m%d')}-{subscription.id[:4]}",
            subtotal=plan.price,
            tax=0,
            total=plan.price,
            status="paid"
        )
        db.add(invoice)
        
    db.commit()
    
    if payment_status == "failed":
        raise HTTPException(status_code=402, detail="Payment Failed")

    return subscription

@router.post("/{subscription_id}/upgrade", response_model=SubscriptionResponse)
def upgrade_subscription(
    subscription_id: str,
    new_plan_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Simplified Proration Logic
    sub = db.query(Subscription).filter(Subscription.id == subscription_id, Subscription.user_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
        
    new_plan = db.query(Plan).filter(Plan.id == new_plan_id).first()
    if not new_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    # In a real system, calculate proration based on days left.
    # Here we simulate an immediate upgrade and charge the full amount of the new plan for simplicity
    sub.plan_id = new_plan.id
    now = datetime.now(timezone.utc)
    
    payment = Payment(
        subscription_id=sub.id,
        amount=new_plan.price,
        status="success",
        gateway="pseudo_stripe_upgrade",
        transaction_id=f"txn_upg_{sub.id}_{now.timestamp()}"
    )
    db.add(payment)
    
    invoice = Invoice(
        user_id=current_user.id,
        subscription_id=sub.id,
        invoice_number=f"INV-UPG-{now.strftime('%Y%m%d')}-{sub.id[:4]}",
        subtotal=new_plan.price,
        tax=0,
        total=new_plan.price,
        status="paid"
    )
    db.add(invoice)
    db.commit()
    db.refresh(sub)
    return sub

@router.post("/{subscription_id}/cancel")
def cancel_subscription(
    subscription_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    sub = db.query(Subscription).filter(Subscription.id == subscription_id, Subscription.user_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    sub.status = "Cancelled"
    db.commit()
    return {"message": "Subscription cancelled"}

@router.post("/{subscription_id}/pay", response_model=SubscriptionResponse)
def retry_payment(
    subscription_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    sub = db.query(Subscription).filter(Subscription.id == subscription_id, Subscription.user_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
        
    now = datetime.now(timezone.utc)
    sub.status = "Active"
    
    payment = Payment(
        subscription_id=sub.id,
        amount=sub.plan.price if sub.plan else 0,
        status="success",
        gateway="pseudo_stripe_retry",
        transaction_id=f"txn_pay_{sub.id}_{now.timestamp()}"
    )
    db.add(payment)
    
    invoice = Invoice(
        user_id=current_user.id,
        subscription_id=sub.id,
        invoice_number=f"INV-REPAY-{now.strftime('%Y%m%d')}-{sub.id[:4]}",
        subtotal=sub.plan.price if sub.plan else 0,
        tax=0,
        total=sub.plan.price if sub.plan else 0,
        status="paid"
    )
    db.add(invoice)
    db.commit()
    db.refresh(sub)
    return sub

@router.get("/me", response_model=List[SubscriptionResponse])
def get_my_subscriptions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    return subs
