from sqlalchemy.orm import Session
from uuid import UUID

from backend.models.interview_config import InterviewConfig
from backend.schemas.interview_config import (
    InterviewConfigCreate,
    InterviewConfigUpdate,
)


#  Create Config
def create_config(
    db: Session,
    company_id: UUID,
    data: InterviewConfigCreate
):
    new_config = InterviewConfig(
        company_id=company_id,
        opening_script=data.opening_script,
        interview_prompt=data.interview_prompt,
        marking_prompt=data.marking_prompt,
        max_questions=data.max_questions,
        max_duration_minutes=data.max_duration_minutes,
        is_active=data.is_active,
        version=data.version,
    )

    try:
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config
    except Exception:
        db.rollback()
        raise


#  List Configs
def list_configs(
    db: Session,
    company_id: UUID
):
    return (
        db.query(InterviewConfig)
        .filter(InterviewConfig.company_id == company_id)
        .all()
    )


#  Get Single Config (Enforces Ownership)
def get_config(
    db: Session,
    company_id: UUID,
    config_id: UUID
):
    config = (
        db.query(InterviewConfig)
        .filter(
            InterviewConfig.id == config_id,
            InterviewConfig.company_id == company_id,
        )
        .first()
    )

    if not config:
        raise ValueError("Interview config not found")

    return config


#  Update Config
def update_config(
    db: Session,
    company_id: UUID,
    config_id: UUID,
    data: InterviewConfigUpdate
):
    config = get_config(db, company_id, config_id)

    update_data = data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(config, field, value)

    try:
        db.commit()
        db.refresh(config)
        return config
    except Exception:
        db.rollback()
        raise


#  Delete Config
def delete_config(
    db: Session,
    company_id: UUID,
    config_id: UUID
):
    config = get_config(db, company_id, config_id)

    try:
        db.delete(config)
        db.commit()
    except Exception:
        db.rollback()
        raise