from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID

from backend.db.session import get_db
from backend.core.dependencies import get_current_company
from backend.models.company import Company
from backend.services import candidate_batch_service


router = APIRouter(
    prefix="/api/v1/candidate-batches",
    tags=["Candidate Batch"]
)


# Upload Batch
@router.post("")
def upload_candidate_batch(
    file: UploadFile = File(...),
    interview_config_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    try:
        return candidate_batch_service.create_candidate_batch(
            db=db,
            company_id=current_company.id,
            interview_config_id=interview_config_id,
            file=file,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Batch Progress
@router.get("/{batch_id}/progress")
def get_batch_progress(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    try:
        return candidate_batch_service.get_batch_progress(
            db=db,
            company_id=current_company.id,
            batch_id=batch_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# List Candidates
@router.get("/candidates")
def list_candidates(
    batch_id: UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    return candidate_batch_service.list_candidates(
        db=db,
        company_id=current_company.id,
        batch_id=batch_id,
        status=status,
        limit=limit,
        offset=offset,
    )