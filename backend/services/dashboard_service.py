from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from backend.models.candidate_batch import CandidateBatch
from backend.models.candidate import Candidate
from backend.models.interview_jobs import InterviewJob


def get_dashboard_summary(
    db: Session,
    company_id: UUID,
):

    total_batches = (
        db.query(func.count(CandidateBatch.id))
        .filter(CandidateBatch.company_id == company_id)
        .scalar()
    )

    total_candidates = (
        db.query(func.count(Candidate.id))
        .filter(Candidate.company_id == company_id)
        .scalar()
    )

    job_status_counts = (
        db.query(
            InterviewJob.status,
            func.count(InterviewJob.id)
        )
        .filter(InterviewJob.company_id == company_id)
        .group_by(InterviewJob.status)
        .all()
    )

    job_summary = {
        "queued": 0,
        "calling": 0,
        "completed": 0,
        "failed": 0,
    }

    for status, count in job_status_counts:
        if status in job_summary:
            job_summary[status] = count

    return {
        "total_batches": total_batches or 0,
        "total_candidates": total_candidates or 0,
        "jobs": job_summary
    }