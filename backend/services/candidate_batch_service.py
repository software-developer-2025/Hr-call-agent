from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from fastapi import UploadFile

from backend.models.candidate import Candidate
from backend.models.candidate_batch import CandidateBatch
from backend.models.interview_jobs import InterviewJob
from backend.models.interview_config import InterviewConfig

from backend.utils.excel_parser import parse_candidate_excel


def create_candidate_batch(
    db: Session,
    company_id: UUID,
    interview_config_id: UUID,
    file: UploadFile,
):
    #  Validate interview config belongs to company
    config = (
        db.query(InterviewConfig)
        .filter(
            InterviewConfig.id == interview_config_id,
            InterviewConfig.company_id == company_id
        )
        .first()
    )

    if not config:
        raise ValueError("Invalid interview_config_id")

    #  Validate file extension
    if not file.filename.endswith((".xlsx", ".csv")):
        raise ValueError("Only .xlsx and .csv files are supported")

    #  Parse Excel
    candidates_data = parse_candidate_excel(file)

    if not candidates_data:
        raise ValueError("Excel file is empty")

    #  Create Batch
    batch = CandidateBatch(
        company_id=company_id,
        filename=file.filename,
        total_records=len(candidates_data),
        status="ready",
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    #  Insert Candidates + Jobs
    for row in candidates_data:

        candidate = Candidate(
            company_id=company_id,
            batch_id=batch.id,
            name=row["name"],
            phone=row["phone"],
            email=row["email"],
            resume_text=row.get("resume_text"),
            experience_years=row["experience_years"],
            status="queued",
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        job = InterviewJob(
            company_id=company_id,
            candidate_id=candidate.id,
            scheduled_time=datetime.utcnow(),
            priority=1,
            status="queued",
        )

        db.add(job)
        db.commit()

    return {
        "batch_id": batch.id,
        "total_records": batch.total_records,
        "status": batch.status
    }