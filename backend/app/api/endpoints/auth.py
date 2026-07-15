from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import UserCreate, UserResponse, Token
from app.models.user import User
from app.models.audit_log import AuditLog
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        name=user_in.name,
        account_type=user_in.account_type,
        organization_name=user_in.organization_name
    )
    db.add(user)
    
    # Audit Logging Feature
    audit = AuditLog(user_id=user.email, action="USER_REGISTERED", details=f"Account Type: {user_in.account_type}")
    db.add(audit)
    
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        # Audit Failed Login
        audit_fail = AuditLog(user_id=form_data.username, action="LOGIN_FAILED", details="Invalid credentials")
        db.add(audit_fail)
        db.commit()
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Audit Successful Login
    audit_success = AuditLog(user_id=user.id, action="LOGIN_SUCCESS", details="User logged in securely")
    db.add(audit_success)
    db.commit()
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(deps.get_current_user)):
    return current_user
