from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.auth import(
    RegisterRequest,
    LoginRequest,
    CompanyResponse,
    LoginResponse,
)
from backend.services import auth_service
from backend.core.dependencies import get_current_company
from backend.models.company import Company


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=CompanyResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        company = auth_service.register_company(
            db=db,
            name=request.name,
            email=request.email,
            password=request.password
        )
        return company

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        token_data = auth_service.login_company(
            db=db,
            email=request.email,
            password=request.password
        )

        return {
            "access_token": token_data["access_token"],
            "token_type": "bearer",
            "company": token_data["company"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=CompanyResponse)
def get_me(
    current_company: Company = Depends(get_current_company)
):
    return current_company