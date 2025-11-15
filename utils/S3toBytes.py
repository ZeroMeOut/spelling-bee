import os
import boto3
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import texttospeech
from botocore.exceptions import ClientError
from utils.credentials import get_google_credentials

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client("s3")

## Initialize Google TTS client
try:
    credentials = get_google_credentials()
    tts_client = texttospeech.TextToSpeechClient(credentials=credentials)
    # print("Google TTS client initialized successfully")
except Exception as e:
    # print(f"Failed to initialize TTS client: {e}")
    tts_client = None

## Generate unique S3 key for audio content
def generate_audio_key(text: str, voice: str = "en-US-Chirp3-HD-Callirrhoe") -> str:
    content_hash = hashlib.md5(f"{text}_{voice}".encode()).hexdigest()
    return f"audio/{content_hash}.mp3"

## Check if audio exists in S3
def check_audio_exists_in_s3(s3_key: str) -> tuple[bool, bytes | None]:
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        audio_bytes = response['Body'].read()
        # print(f"Found existing audio in S3: {s3_key}")
        return True, audio_bytes
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # print(f"Audio not found in S3: {s3_key}")
            return False, None
        else:
            raise

## Generate and save audio to S3
def generate_and_save_audio(text: str, s3_key: str, voice: str = "en-US-Chirp3-HD-Callirrhoe") -> bytes:
    # print(f"Generating new audio for: {text}")
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=voice.split("-")[0] + "-" + voice.split("-")[1],
        name=voice
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    ## Pylance false positive here
    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice_params,
        audio_config=audio_config
    )
    
    audio_bytes = response.audio_content
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=audio_bytes,
        ContentType='audio/mpeg',
        Metadata={
            'text': text,
            'voice': voice,
            'generated_at': datetime.now().isoformat()
        }
    )
    
    # print(f"Saved audio to S3: {s3_key}")
    
    return audio_bytes

def generate_audio_for_text(text: str, voice: str = "en-US-Chirp3-HD-Callirrhoe") -> bytes:
    s3_key = generate_audio_key(text, voice)
    exists, audio_bytes = check_audio_exists_in_s3(s3_key)
    if exists and audio_bytes is not None:
        return audio_bytes
    else:
        return generate_and_save_audio(text, s3_key, voice)


if __name__ == "__main__":
    sample_word = "notes"
    audio_data = generate_audio_for_text(sample_word)
    print(f"Retrieved {len(audio_data)} bytes for word '{sample_word}'")

    ## To save the audio bytes to a file for testing
    with open(f"{sample_word}.mp3", "wb") as f:
        f.write(audio_data)
    print(f"Saved audio to {sample_word}.mp3")