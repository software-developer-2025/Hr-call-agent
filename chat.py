import os
from dotenv import load_dotenv
from io import BytesIO
import requests

from google import genai
from elevenlabs.client import ElevenLabs
from elevenlabs import play

load_dotenv()

client = genai.Client(os.getenv("GOOGLE_API_KEY"))
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"),)


def generate_bot_reply(user_text: str) -> str:
    """
    Takes real user speech (converted to text)
    and returns a short, voice-friendly response.
    """

    prompt = f"""
    You are a friendly AI voice assistant speaking to a user.
        Rules:
        - Respond like a human having a natural conversation
        - Keep responses short and clear (1-3 sentences)
        - Sound calm, helpful, and friendly
    User said:
    "{user_text}"
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text.strip()


#  MAIN PIPELINE 
def voice_to_voice(audio_bytes: bytes):
    """
    Full pipeline:
    Voice → Text → LLM → Text → Voice
    """

    audio_data = BytesIO(audio_bytes)

    #  SPEECH → TEXT 
    transcription = elevenlabs.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v2",
        tag_audio_events=True,
        language_code="eng",
        diarize=True,
    )

    user_text = transcription.text.strip()
    print("USER (STT):", user_text)

    if not user_text:
        return

    #  TEXT → TEXT (LLM) 
    bot_text = generate_bot_reply(user_text)
    print("BOT (LLM):", bot_text)

    #  TEXT → SPEECH 
    audio = elevenlabs.text_to_speech.convert(
        text=bot_text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    play(audio)

#  TEST INPUT 
if __name__ == "__main__":
    # Example audio source (replace with mic / Twilio stream)
    audio_url = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
    audio_bytes = requests.get(audio_url).content

    voice_to_voice(audio_bytes)
   