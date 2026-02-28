from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_company(db: Session, name: str, email: str, password: str):
    existing_company = (db.query(Company).filter(Company.email == email).first())

    if existing_company:
        raise ValueError("Email already registered")

    hashed_password = hash_password(password)

    new_company = Company(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


def login_company(db: Session, email: str, password: str):
    company = (db.query(Company).filter(Company.email == email).first())

    if not company:
        raise ValueError("Invalid credentials")

    if not verify_password(password, company.password_hash):
        raise ValueError("Invalid credentials")

    if company.status != "active":
        raise ValueError("Account is suspended")
    
    access_token = create_access_token(
        {"company_id": str(company.id)}
    )

    return {
        "access_token": access_token,
        "company": company
    }