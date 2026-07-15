from fastapi import APIRouter
from app.api.endpoints import auth, plans, subscriptions, admin, invoices, webhooks

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
