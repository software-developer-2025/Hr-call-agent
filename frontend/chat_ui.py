import uuid
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from mistralai import Mistral


load_dotenv()


gemini = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
model = "ministral-3b-latest"
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def generate_bot_reply(user_text: str) -> str:
    prompt = f"""
You are a friendly AI voice assistant speaking to a user.

Rules:
- Speak naturally
- Keep replies short (1–3 sentences)
- Calm, helpful, friendly tone
- No emojis, no lists

User said:
"{user_text}"
"""

    response = client.chat.complete(
        model="ministral-3b-latest",
        messages=[
        {
            "role": "user",
            "content":prompt,
        },
    ],
    )
    return response.choices[0].message.content.strip()

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="🎤 Voice Chatbot", layout="centered")
st.title("🎤 AI Voice Chatbot")
st.write("Click the mic, speak, and get a spoken reply.")

# ---------- MIC INPUT (BUILT-IN) ----------
audio_bytes = st.audio_input("🎙️ Speak")

if audio_bytes is not None:
    try:
        st.success("Voice received")

        audio_data = BytesIO(audio_bytes.getvalue())

        # ---------- SPEECH → TEXT ----------
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v2",
            language_code="eng",
        )

        if not transcription or not transcription.text:
            st.error("No speech detected. Please speak clearly.")
            st.stop()

        user_text = transcription.text.strip()
        st.markdown(f"**You:** {user_text}")

        # ---------- TEXT → TEXT ----------
        bot_text = generate_bot_reply(user_text)
        st.markdown(f"**Bot:** {bot_text}")

        
        # ---------- TEXT → SPEECH ----------
        audio_generator = elevenlabs.text_to_speech.convert(
            text=bot_text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        audio_bytes = b"".join(audio_generator)

        st.audio(audio_bytes, format="audio/mp3")


    except Exception as e:
        st.error("Something went wrong while processing your request.")
        st.exception(e) 
