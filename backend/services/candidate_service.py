from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from backend.models.candidate import Candidate
from backend.models.interview_jobs import InterviewJob



# GET SINGLE CANDIDATE

def get_candidate(
    db: Session,
    company_id: UUID,
    candidate_id: UUID,
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id,
            Candidate.company_id == company_id
        )
        .first()
    )

    if not candidate:
        raise ValueError("Candidate not found")

    job = (
        db.query(InterviewJob)
        .filter(
            InterviewJob.candidate_id == candidate.id,
            InterviewJob.company_id == company_id
        )
        .first()
    )

    return {
        "candidate": candidate,
        "interview_job": job
    }



# UPDATE CANDIDATE (Reschedule / Status Change)
def update_candidate(
    db: Session,
    company_id: UUID,
    candidate_id: UUID,
    status: str | None = None,
    scheduled_time: datetime | None = None,
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id,
            Candidate.company_id == company_id
        )
        .first()
    )

    if not candidate:
        raise ValueError("Candidate not found")

    if status:
        candidate.status = status

    job = (
        db.query(InterviewJob)
        .filter(
            InterviewJob.candidate_id == candidate.id,
            InterviewJob.company_id == company_id
        )
        .first()
    )

    if job and scheduled_time:
        job.scheduled_time = scheduled_time

    db.commit()
    db.refresh(candidate)

    return candidate