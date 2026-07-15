from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas import PlanResponse
from app.models.plan import Plan

router = APIRouter()

@router.get("/", response_model=List[PlanResponse])
def read_plans(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100):
    plans = db.query(Plan).filter(Plan.active == True).offset(skip).limit(limit).all()
    return plans
