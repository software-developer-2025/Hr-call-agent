import os
import json
import pdfplumber
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from mistralai import Mistral

# ---------------- LOAD ENV ----------------
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- TWILIO ----------------
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TO_NUMBER = os.getenv("TO_NUMBER")
VOICE_WEBHOOK_URL = os.getenv("VOICE_WEBHOOK_URL")

# ---------------- MISTRAL ----------------
mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# ---------------- GLOBAL STATE ----------------
CALL_STATE = {}

# ---------------- RESUME EXTRACTION ----------------
def extract_resume_text(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text.strip()

RESUME_TEXT = extract_resume_text("static/entry_level_resume.pdf")

MAX_QUESTIONS = 5

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = f"""
You are a strict HR technical interviewer.

RULES:
- Use ONLY resume information
- Ask ONLY technical questions
- Ask ONE question at a time
- NEVER repeat a question
- Do NOT give hints or feedback
- Be formal and concise

Resume:
{RESUME_TEXT}
"""

# ---------------- LOGGING ----------------
def log(call_sid, speaker, text):
    print(f"[{call_sid}] {speaker}: {text}")

# ---------------- OUTBOUND CALL ----------------
@app.get("/call")
def make_call():
    call = twilio_client.calls.create(
        to=TO_NUMBER,
        from_=FROM_NUMBER,
        url=VOICE_WEBHOOK_URL,
        method="POST"
    )
    return {"call_sid": call.sid}

# ---------------- VOICE ENTRY (COMPANY INTRO) ----------------
@app.post("/voice")
async def voice():
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/process",
        method="POST",
        timeout=6,
        speechTimeout="none"
    )

    gather.say(
        "Hello. This is the Human Resources interview system of Steve’s AI Lab Private Limited. "
        "Your resume has been shortlisted for a technical position. "
        "This will be a short telephonic technical interview. "
        "We will start with easy questions and gradually increase the difficulty. "
        "Please answer clearly after each question. "
        "Are you ready to begin the interview?"
    )

    response.append(gather)
    return Response(str(response), media_type="application/xml")

# ---------------- PROCESS ----------------
@app.post("/process")
async def process(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid")
    user_text = (form.get("SpeechResult") or "").strip()

    response = VoiceResponse()

    if call_sid not in CALL_STATE:
        CALL_STATE[call_sid] = {
            "consented": False,
            "asked": 0,
            "questions": [],
            "scores": []
        }

    state = CALL_STATE[call_sid]

    # ---- CONSENT ----
    if not state["consented"]:
        log(call_sid, "USER", user_text)
        if "yes" not in user_text.lower():
            response.say("Thank you for your time. Goodbye.")
            response.hangup()
            return Response(str(response), media_type="application/xml")
        state["consented"] = True

    # ---- STOP CONDITION ----
    if state["asked"] >= MAX_QUESTIONS:
        response.say(
            "Thank you for attending the interview. "
            "Our HR team will contact you if you are shortlisted. Goodbye."
        )
        response.hangup()
        return Response(str(response), media_type="application/xml")

    # ---- DIFFICULTY ----
    if state["asked"] == 0:
        difficulty = "EASY"
    elif state["asked"] <= 2:
        difficulty = "MEDIUM"
    else:
        difficulty = "HARD"

    asked_block = "\n".join(f"- {q}" for q in state["questions"])

    question_prompt = f"""
Difficulty level: {difficulty}

Already asked questions:
{asked_block}

Instructions:
- EASY: simple explanation or overview from resume, ask about programming language knowledge
- MEDIUM: implementation details
- HARD: design decisions, trade-offs, edge cases

Ask ONE new technical interview question.
Do NOT repeat or paraphrase previous questions.
"""

    llm_response = mistral.chat.complete(
        model="mistral-small",
        temperature=0.5,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question_prompt}
        ]
    )

    question = llm_response.choices[0].message.content.strip()

    state["questions"].append(question)
    state["asked"] += 1

    log(call_sid, "HR", f"[{difficulty}] {question}")

    gather = Gather(
        input="speech",
        action="/evaluate",
        method="POST",
        timeout=15,
        speechTimeout="none"
    )

    gather.say(question)
    response.append(gather)

    return Response(str(response), media_type="application/xml")

# ---------------- EVALUATE ----------------
@app.post("/evaluate")
async def evaluate(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid")
    answer = (form.get("SpeechResult") or "").strip()

    log(call_sid, "ANSWER", answer)

    evaluation_prompt = f"""
Evaluate the following technical answer.

Answer:
{answer}

Return STRICT JSON:
{{
  "relevance": 0-10,
  "correctness": 0-10,
  "clarity": 0-10
}}
"""

    llm_eval = mistral.chat.complete(
        model="mistral-small",
        temperature=0.5,
        messages=[{"role": "system", "content": evaluation_prompt}]
    )

    try:
        score = json.loads(llm_eval.choices[0].message.content)
    except Exception:
        score = {"relevance": 0, "correctness": 0, "clarity": 0}

    CALL_STATE[call_sid]["scores"].append(score)
    print("SCORE:", score)

    response = VoiceResponse()
    response.redirect("/process")
    return Response(str(response), media_type="application/xml")
