# Hr-call-agent

# 🎯 Core System: General Interview Marking Agent


🔹 1. Organization Onboarding (UI)

Organization provides:

Company Name

Interview Script (Intro message)

Interview Criteria (technical, communication, etc.)

Marking Rubric (weightage)

Question Bank or Prompt Template

Difficulty level logic

Call time window

You store this as:

Organization
InterviewConfig
QuestionSet
EvaluationRubric


# 📞 2. Bulk Candidate Calling (CSV Upload)

CSV fields:

name, phone, email, role, experience, resume


Flow:

Upload CSV
→ Validate numbers
→ Queue candidates
→ Loop calls one by one
→ Update status after each attempt

Call Status Types:

📞 Received

🎤 Interviewed

❌ Not Answered

🚫 Declined

🔁 Requested Another Slot

📅 Rescheduled

⚠️ Invalid Number

🧠 3. Dynamic Interview Engine

For each candidate:

Play organization intro script

Ask questions (from org config)

Record responses

Evaluate using provided rubric

Assign marks per criteria

Store transcript + scoring breakdown

Example scoring JSON:

{
  "technical": 8,
  "communication": 6,
  "problem_solving": 7,
  "confidence": 5,
  "overall": 6.5
}

# 🧠 3. Dynamic Interview Engine

For each candidate:

Play organization intro script

Ask questions (from org config)

Record responses

Evaluate using provided rubric

Assign marks per criteria

Store transcript + scoring breakdown

Example scoring JSON:

{
  "technical": 8,
  "communication": 6,
  "problem_solving": 7,
  "confidence": 5,
  "overall": 6.5
}

# 🚀 Advanced Features You Can Add
1️⃣ Adaptive Questioning

If candidate answers well → increase difficulty
If struggling → reduce difficulty

2️⃣ Real-Time Sentiment Analysis

Track:

Confidence

Nervousness

Clarity

Tone stability

3️⃣ Cheating Detection

Long unnatural pauses

Background voices

Reading tone pattern

4️⃣ Interview Summary Generator

Auto-generate:

Strengths

Weaknesses

Hire/No-hire recommendation

5️⃣ Reschedule Automation

If declined:

Send SMS with booking link

Auto requeue

6️⃣ Ranking System

Auto-rank candidates per campaign

7️⃣ Multi-language Support

Ask in Hindi / English / regional languages

8️⃣ Panel Mode

Multiple AI evaluators:

Technical AI

HR AI

Communication AI
Then aggregate final score

🏗 Suggested System Architecture

UI (React / Streamlit)
↓
Backend (FastAPI)
↓
Task Queue (Celery / Redis)
↓
Twilio Call Service
↓
LLM Evaluation Engine
↓
Database (Postgres)
↓
Reporting Dashboard

# 🛡 Enterprise-Level Add-ons

Role-based access control (HR, Admin, Reviewer)

Call retry logic (3 attempts rule)

Rate limiting

Call time zone detection

Blacklist system

Data encryption

GDPR consent handling
