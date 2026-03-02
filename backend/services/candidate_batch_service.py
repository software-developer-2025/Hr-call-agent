from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile

from backend.models.candidate import Candidate
from backend.models.candidate_batch import CandidateBatch
from backend.models.interview_jobs import InterviewJob
from backend.models.interview_config import InterviewConfig

from backend.utils.excel_parser import parse_candidate_excel



# CREATE BATCH

def create_candidate_batch(
    db: Session,
    company_id: UUID,
    interview_config_id: UUID,
    file: UploadFile,
):

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

    if not file.filename.endswith((".xlsx", ".csv")):
        raise ValueError("Only .xlsx and .csv files are supported")

    parsed = parse_candidate_excel(file)

    valid_rows = parsed["valid_rows"]
    errors = parsed["errors"]

    if not valid_rows and errors:
        batch_status = "failed"
    elif errors:
        batch_status = "partially_failed"
    else:
        batch_status = "queued"

    try:
        batch = CandidateBatch(
            company_id=company_id,
            filename=file.filename,
            total_records=len(valid_rows),
            status=batch_status,
        )

        db.add(batch)
        db.flush()

        candidates = []

        for row in valid_rows:
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
            candidates.append(candidate)

        db.add_all(candidates)
        db.flush()

        jobs = []

        for candidate in candidates:
            job = InterviewJob(
                company_id=company_id,
                candidate_id=candidate.id,
                scheduled_time=datetime.utcnow(),
                priority=1,
                status="queued",
            )
            jobs.append(job)

        db.add_all(jobs)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "batch_id": batch.id,
        "total_valid": len(valid_rows),
        "total_invalid": len(errors),
        "status": batch_status,
        "errors": errors
    }



# BATCH PROGRESS

def get_batch_progress(
    db: Session,
    company_id: UUID,
    batch_id: UUID
):

    batch = (
        db.query(CandidateBatch)
        .filter(
            CandidateBatch.id == batch_id,
            CandidateBatch.company_id == company_id
        )
        .first()
    )

    if not batch:
        raise ValueError("Batch not found")

    status_counts = (
        db.query(
            Candidate.status,
            func.count(Candidate.id)
        )
        .filter(
            Candidate.batch_id == batch_id,
            Candidate.company_id == company_id
        )
        .group_by(Candidate.status)
        .all()
    )

    progress = {
        "queued": 0,
        "calling": 0,
        "completed": 0,
        "failed": 0,
    }

    for status, count in status_counts:
        if status in progress:
            progress[status] = count

    total = sum(progress.values())

    percentage = 0
    if total > 0:
        percentage = round(
            (progress["completed"] / total) * 100,
            2
        )

    return {
        "batch_id": batch.id,
        "batch_status": batch.status,
        "total_candidates": total,
        "progress": progress,
        "completion_percentage": percentage
    }


# LIST CANDIDATES

def list_candidates(
    db: Session,
    company_id: UUID,
    batch_id: UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
):

    query = db.query(Candidate).filter(
        Candidate.company_id == company_id
    )

    if batch_id:
        query = query.filter(Candidate.batch_id == batch_id)

    if status:
        query = query.filter(Candidate.status == status)

    total = query.count()

    candidates = (
        query
        .order_by(Candidate.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": candidates
    }