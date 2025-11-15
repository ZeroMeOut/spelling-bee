import json
import boto3
from google.oauth2 import service_account
from functools import lru_cache

## Claude generated this function to fetch Google credentials from AWS Secrets Manager
@lru_cache(maxsize=1)
def get_google_credentials() -> service_account.Credentials:
    """
    Fetch Google Cloud credentials from AWS Secrets Manager.
    Cached to avoid repeated API calls.
    """
    secret_name = "google-tts-credentials"
    region_name = "us-east-1"
    
    # Create a Secrets Manager client
    session = boto3.session.Session() ## Idk why pylance shows an error here
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        raise Exception(f"Error retrieving secret: {str(e)}")
    
    # Parse the secret
    secret = get_secret_value_response['SecretString']
    secret_dict = json.loads(secret)
    
    # Create credentials object
    credentials = service_account.Credentials.from_service_account_info(
        secret_dict
    )
    
    return credentials

if __name__ == "__main__":
    creds = get_google_credentials()

    print(creds)
    print("Successfully retrieved Google credentials.")