from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.core.dependencies import get_current_company
from backend.models.company import Company
from backend.services import dashboard_service


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    return dashboard_service.get_dashboard_summary(
        db=db,
        company_id=current_company.id
    )