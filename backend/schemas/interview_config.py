from pydantic import BaseModel, Field
from typing import Optional

from datetime import datetime
from uuid import UUID


from pydantic import BaseModel, Field
from typing import Optional


class InterviewConfigCreate(BaseModel):
    opening_script: str = Field(..., min_length=10)
    interview_prompt: str = Field(..., min_length=10)
    marking_prompt: str = Field(..., min_length=10)
    max_questions: int = Field(..., gt=0)
    max_duration_minutes: int = Field(..., gt=0)
    is_active: Optional[bool] = True
    version: Optional[int] = 1
   

class InterviewConfigResponse(BaseModel):
    id: UUID
    opening_script: str
    interview_prompt: str
    marking_prompt: str
    max_questions: int
    max_duration_minutes: int
    is_active: bool
    version: int
    created_at: datetime

    class Config:
        from_attributes = True
        

class InterviewConfigUpdate(BaseModel):
    opening_script: Optional[str] = Field(None, min_length=10)
    interview_prompt: Optional[str] = Field(None, min_length=10)
    marking_prompt: Optional[str] = Field(None, min_length=10)
    max_questions: Optional[int] = Field(None, gt=0)
    max_duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    version: Optional[int] = None
    

class DeleteConfigResponse(BaseModel):
    id: UUID
    message: str