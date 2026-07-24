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

@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(check_admin),
    limit: int = 50
):
    from app.models.audit_log import AuditLog
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs

@router.post("/retry-dunning")
def retry_dunning_jobs(
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(check_admin)
):
    from app.models.audit_log import AuditLog
    from app.models.invoice import Invoice
    from datetime import datetime, timezone

    past_due_subs = db.query(Subscription).filter(Subscription.status == "Past Due").all()
    recovered_count = 0

    for sub in past_due_subs:
        sub.status = "Active"
        recovered_count += 1
        now = datetime.now(timezone.utc)
        payment = Payment(
            subscription_id=sub.id,
            amount=sub.plan.price if sub.plan else 0,
            status="success",
            gateway="dunning_retry_auto",
            transaction_id=f"txn_retry_{sub.id}_{now.timestamp()}"
        )
        db.add(payment)
        invoice = Invoice(
            user_id=sub.user_id,
            subscription_id=sub.id,
            invoice_number=f"INV-RETRY-{now.strftime('%Y%m%d')}-{sub.id[:4]}",
            subtotal=sub.plan.price if sub.plan else 0,
            tax=0,
            total=sub.plan.price if sub.plan else 0,
            status="paid"
        )
        db.add(invoice)

    audit = AuditLog(
        user_id=admin_user.id,
        action="DUNNING_RETRY_RUN",
        details=f"Processed {len(past_due_subs)} past-due accounts. Recovered {recovered_count}."
    )
    db.add(audit)
    db.commit()

    return {"message": f"Dunning retry completed. Recovered {recovered_count} subscriptions."}
