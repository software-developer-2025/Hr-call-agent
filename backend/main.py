from fastapi import FastAPI

from backend.db.base import Base
from backend.db.session import engine
from backend.routes import auth, interview_config, candidate_batch, candidate, dashboard


# Create tables (DEV only)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(auth.router)
app.include_router(interview_config.router)
app.include_router(candidate_batch.router)
app.include_router(candidate.router)
app.include_router(dashboard.router)