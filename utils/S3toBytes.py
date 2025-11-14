import os
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client("s3")

def get_presigned_audio_bytes(word: str):
    file_key = f"audio/{word}.wav"
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": file_key},
        ExpiresIn=300  # 5 minutes
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.content


if __name__ == "__main__":
    sample_word = "example"
    audio_data = get_presigned_audio_bytes(sample_word)
    print(f"Retrieved {len(audio_data)} bytes for word '{sample_word}'")

    ## To save the audio bytes to a file for testing
    with open(f"{sample_word}.wav", "wb") as f:
        f.write(audio_data)
    print(f"Saved audio to {sample_word}.wav")