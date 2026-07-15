import logging
import os
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.plan import Plan
from app.models.user import User
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # Drop and recreate for development
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed Plans
    plans = [
        {"name": "Free", "price": 0, "description": "Basic features, limited access.", "billing_cycle": "monthly"},
        {"name": "Starter", "price": 29900, "description": "Good for small projects.", "billing_cycle": "monthly"},
        {"name": "Pro", "price": 99900, "description": "All professional features included.", "billing_cycle": "monthly"},
        {"name": "Enterprise", "price": 299900, "description": "Dedicated support and unlimited access.", "billing_cycle": "monthly"},
    ]
    
    for plan_data in plans:
        new_plan = Plan(**plan_data)
        db.add(new_plan)
            
    # Seed a demo admin user
    demo_admin = User(
        name="Admin",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        verified=True,
        account_type="organization",
        role="admin"
    )
    db.add(demo_admin)
    
    # Seed a demo customer user
    demo_customer = User(
        name="Alice Demo",
        email="alice@example.com",
        password_hash=get_password_hash("password123"),
        verified=True,
        account_type="individual",
        role="customer"
    )
    db.add(demo_customer)
        
    db.commit()

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
