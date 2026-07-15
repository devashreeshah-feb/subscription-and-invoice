from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.audit_log import AuditLog
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(deps.get_db)):
    """
    Mock Stripe Webhook endpoint. 
    In production, this would verify the Stripe signature securely.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")
        
    event_type = payload.get("type")
    
    # Feature 12 & 14: Log webhook event as an Audit Log
    audit = AuditLog(
        user_id="system", 
        action=f"WEBHOOK_RECEIVED: {event_type}",
        details=str(payload)
    )
    db.add(audit)
    db.commit()
    
    # Process event
    if event_type == "invoice.payment_succeeded":
        logger.info("Payment succeeded via webhook")
        # Logic to activate subscription...
    elif event_type == "invoice.payment_failed":
        logger.info("Payment failed via webhook - Init Dunning process")
        # Trigger Dunning worker...
        
    return {"status": "success"}
