import time
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from sqlalchemy.exc import SQLAlchemyError

from backend.db.session import SessionLocal
from backend.models.interview_jobs import InterviewJob
from backend.models.candidate import Candidate
from backend.models.interview_config import InterviewConfig
from backend.models.candidate_batch import CandidateBatch


MAX_RETRIES = 3
MAX_CONCURRENT_PER_COMPANY = 5
SLEEP_INTERVAL = 2

IST = ZoneInfo("Asia/Kolkata")


def simulate_interview_execution():
    return random.random() < 0.8


def fetch_next_job(db: Session):
    now_utc = datetime.utcnow()

    stmt = (
        select(InterviewJob)
        .where(
            InterviewJob.status == "queued",
            InterviewJob.scheduled_time <= now_utc,
            or_(
                InterviewJob.retry_at == None,
                InterviewJob.retry_at <= now_utc
            )
        )
        .order_by(InterviewJob.created_at.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    )

    return db.execute(stmt).scalars().first()


def is_within_call_window(config: InterviewConfig):
    now_ist = datetime.now(IST).time()
    return config.call_start_time <= now_ist <= config.call_end_time


def company_under_limit(db: Session, company_id):
    active_count = (
        db.query(func.count(InterviewJob.id))
        .filter(
            InterviewJob.company_id == company_id,
            InterviewJob.status == "calling"
        )
        .scalar()
    )

    return active_count < MAX_CONCURRENT_PER_COMPANY


def schedule_retry(job: InterviewJob):
    job.retry_count += 1

    if job.retry_count >= MAX_RETRIES:
        job.status = "failed"
        return

    delay_seconds = 60 * (2 ** job.retry_count)
    job.retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
    job.status = "queued"


def update_batch_status(db: Session, batch_id):
    total = (
        db.query(func.count(Candidate.id))
        .filter(Candidate.batch_id == batch_id)
        .scalar()
    )

    completed = (
        db.query(func.count(Candidate.id))
        .filter(
            Candidate.batch_id == batch_id,
            Candidate.status == "completed"
        )
        .scalar()
    )

    failed = (
        db.query(func.count(Candidate.id))
        .filter(
            Candidate.batch_id == batch_id,
            Candidate.status == "failed"
        )
        .scalar()
    )

    batch = (
        db.query(CandidateBatch)
        .filter(CandidateBatch.id == batch_id)
        .first()
    )

    if not batch or total == 0:
        return

    if completed == total:
        batch.status = "completed"
    elif failed == total:
        batch.status = "failed"
    elif completed + failed == total:
        batch.status = "partially_completed"
    else:
        batch.status = "processing"

    db.commit()


def process_job(db: Session, job: InterviewJob):
    try:
        job.status = "calling"
        db.commit()

        print(f"[{datetime.utcnow()}] Job {job.id} started")

        success = simulate_interview_execution()

        candidate = (
            db.query(Candidate)
            .filter(Candidate.id == job.candidate_id)
            .first()
        )

        if success:
            job.status = "completed"
            if candidate:
                candidate.status = "completed"
            print(f"[{datetime.utcnow()}] Job {job.id} completed")

        else:
            schedule_retry(job)

            if job.status == "failed":
                if candidate:
                    candidate.status = "failed"
                print(f"[{datetime.utcnow()}] Job {job.id} permanently failed")
            else:
                print(f"[{datetime.utcnow()}] Job {job.id} retry scheduled")

        db.commit()

        # 🔥 Update batch status after final result
        if candidate and job.status in ["completed", "failed"]:
            update_batch_status(db, candidate.batch_id)

    except SQLAlchemyError as e:
        db.rollback()
        job.status = "failed"
        job.last_error = str(e)
        db.commit()
        print(f"[{datetime.utcnow()}] Job {job.id} crashed")


def worker_loop():
    print("Production-grade worker started...")

    while True:
        db = SessionLocal()

        try:
            job = fetch_next_job(db)

            if not job:
                time.sleep(SLEEP_INTERVAL)
                continue

            config = (
                db.query(InterviewConfig)
                .filter(InterviewConfig.id == job.interview_config_id)
                .first()
            )

            if not config:
                job.status = "failed"
                job.last_error = "Missing interview config"
                db.commit()
                continue

            # Office hours check (IST)
            if not is_within_call_window(config):
                time.sleep(SLEEP_INTERVAL)
                continue

            # Company rate limit
            if not company_under_limit(db, job.company_id):
                time.sleep(SLEEP_INTERVAL)
                continue

            process_job(db, job)

        except Exception as e:
            print("Worker error:", e)

        finally:
            db.close()


if __name__ == "__main__":
    worker_loop()