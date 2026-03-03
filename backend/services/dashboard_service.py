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

    # Total batches
    total_batches = (
        db.query(func.count(CandidateBatch.id))
        .filter(CandidateBatch.company_id == company_id)
        .scalar()
    )

    # Total candidates
    total_candidates = (
        db.query(func.count(Candidate.id))
        .filter(Candidate.company_id == company_id)
        .scalar()
    )

    # Job status aggregation
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

    total_jobs = sum(job_summary.values())

    completion_percentage = 0
    if total_jobs > 0:
        completion_percentage = round(
            (job_summary["completed"] / total_jobs) * 100,
            2
        )

    return {
        "total_batches": total_batches or 0,
        "total_candidates": total_candidates or 0,
        "total_jobs": total_jobs,
        "completion_percentage": completion_percentage,
        "jobs": job_summary
    }