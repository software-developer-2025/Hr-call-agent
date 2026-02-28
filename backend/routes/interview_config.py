from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.db.session import get_db
from backend.schemas.interview_config import (
    InterviewConfigCreate,
    InterviewConfigUpdate,
    InterviewConfigResponse,
    DeleteConfigResponse
)
from backend.services import interview_config_service
from backend.core.dependencies import get_current_company
from backend.models.company import Company


router = APIRouter(
    prefix="/api/v1/interview-configs",
    tags=["Interview Config"]
)


# Create
@router.post("/create", response_model=InterviewConfigResponse)
def create_config(
    request: InterviewConfigCreate,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    try:
        return interview_config_service.create_config(
            db=db,
            company_id=current_company.id,
            data=request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

 
# List
@router.get("/list", response_model=List[InterviewConfigResponse])
def list_configs(
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    try:
        return interview_config_service.list_configs(
            db=db,
            company_id=current_company.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get One
@router.get("/get/{config_id}", response_model=InterviewConfigResponse)
def get_config(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    try:
        return interview_config_service.get_config(
            db=db,
            company_id=current_company.id,
            config_id=config_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Update
@router.patch("/update/{config_id}", response_model=InterviewConfigResponse)
def update_config(
    config_id: UUID,
    request: InterviewConfigUpdate,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    try:
        return interview_config_service.update_config(
            db=db,
            company_id=current_company.id,
            config_id=config_id,
            data=request
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Delete
@router.delete("/delete/{config_id}", response_model=DeleteConfigResponse)
def delete_config(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    try:
        interview_config_service.delete_config(
            db=db,
            company_id=current_company.id,
            config_id=config_id
        )

        return {
            "id": config_id,
            "message": f"{config_id} has been successfully deleted"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))