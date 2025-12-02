import logging
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Define the OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    "https://www.googleapis.com/auth/calendar"
]


def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        "service.json", scopes=SCOPES
    )
    return creds

# Authenticate and build the service
def authenticate_oauth():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        creds_json = creds.to_json()
        logging.info(f"Using credentials from token.json, expires {creds.expiry}")
        logging.info(f"Using credentials from token.json {creds.to_json()}")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logging.info(f"Refreshed credentials, expires {creds.expiry}")
            logging.info(f"Refreshed credentials: {creds.to_json()}")
        else:
            if not creds:
                logging.info(f"Token: {creds.to_json()}")
            else:
                logging.info("no token")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0,access_type='offline')
        # Save token for next time
        with open('token.json', 'w') as token:
            creds_json = creds.to_json()
            token.write(creds_json)
            logging.info(f"Saved credentials to token.json {creds_json.get('expiry')}")

    return creds
