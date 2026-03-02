from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from backend.db.session import get_db
from backend.core.dependencies import get_current_company
from backend.models.company import Company
from backend.services import candidate_service


router = APIRouter(
    prefix="/api/v1/candidates",
    tags=["Candidates"]
)


# GET SINGLE CANDIDATE
@router.get("/{candidate_id}")
def get_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    try:
        return candidate_service.get_candidate(
            db=db,
            company_id=current_company.id,
            candidate_id=candidate_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



# UPDATE CANDIDATE
@router.patch("/{candidate_id}")
def update_candidate(
    candidate_id: UUID,
    status: str | None = None,
    scheduled_time: datetime | None = None,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    try:
        return candidate_service.update_candidate(
            db=db,
            company_id=current_company.id,
            candidate_id=candidate_id,
            status=status,
            scheduled_time=scheduled_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))