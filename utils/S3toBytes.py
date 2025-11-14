import os
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client("s3")

def get_presigned_audio_bytes(word: str):
    file_key = f"audio/{word}.wav"
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        return response['Body'].read()
    except Exception as e:
        print(f"Error getting audio for '{word}': {e}")
        print(f"Bucket: {bucket_name}, Key: {file_key}")
        raise


if __name__ == "__main__":
    sample_word = "example"
    audio_data = get_presigned_audio_bytes(sample_word)
    print(f"Retrieved {len(audio_data)} bytes for word '{sample_word}'")

    ## To save the audio bytes to a file for testing
    with open(f"{sample_word}.wav", "wb") as f:
        f.write(audio_data)
    print(f"Saved audio to {sample_word}.wav")