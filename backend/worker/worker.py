import time
import random
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.db.session import SessionLocal
from backend.models.interview_jobs import InterviewJob
from backend.models.candidate import Candidate


MAX_RETRIES = 3
SLEEP_INTERVAL = 2


def simulate_interview_execution():
    # 80% success
    return random.random() < 0.8


def fetch_next_job(db: Session):
    """
    Fetch next queued job safely using row locking.
    Prevents multiple workers from picking same job.
    """

    stmt = (
        select(InterviewJob)
        .where(
            InterviewJob.status == "queued",
            InterviewJob.scheduled_time <= datetime.utcnow(),
        )
        .order_by(InterviewJob.created_at.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    )

    result = db.execute(stmt).scalars().first()
    return result


def process_job(db: Session, job: InterviewJob):

    try:
        job.status = "calling"
        db.commit()

        success = simulate_interview_execution()

        candidate = db.query(Candidate).filter(
            Candidate.id == job.candidate_id
        ).first()

        if success:
            job.status = "completed"
            if candidate:
                candidate.status = "completed"

        else:
            job.retry_count += 1
            job.last_error = "Mock execution failure"

            if job.retry_count >= MAX_RETRIES:
                job.status = "failed"
                if candidate:
                    candidate.status = "failed"
            else:
                job.status = "queued"

        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        job.status = "failed"
        job.last_error = str(e)
        db.commit()


def worker_loop():

    print("Production-safe worker started...")

    while True:
        db = SessionLocal()

        try:
            job = fetch_next_job(db)

            if job:
                print(f"Processing job {job.id}")
                process_job(db, job)
            else:
                time.sleep(SLEEP_INTERVAL)

        except Exception as e:
            print("Worker error:", e)

        finally:
            db.close()


if __name__ == "__main__":
    worker_loop()