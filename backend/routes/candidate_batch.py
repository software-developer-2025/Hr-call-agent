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

@router.post("")
def upload_candidate_batch(
    file: UploadFile = File(...),
    interview_config_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    try:
        result = candidate_batch_service.create_candidate_batch(
            db=db,
            company_id=current_company.id,
            interview_config_id=interview_config_id,
            file=file,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    