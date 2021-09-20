import os
import pickle
import requests
from secrets import refresh_token, base_64
from google.auth import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


class Refresh:

    def __init__(self):
        self.refresh_token = refresh_token
        self.base_64 = base_64
        self.credentials = credentials

    def refresh(self):
        
        query = "https://accounts.spotify.com/api/token"
        response = requests.post(query, data = {"grant_type": "refresh_token", "refresh_token": refresh_token},
                                        headers = {"Authorization": "Basic " + base_64})

        response_json = response.json()
        return response_json["access_token"]

    def YTcredentials(self):
        
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", 
                scopes = ['https://www.googleapis.com/auth/youtube.readonly'])
                flow.run_local_server(port = 8080, prompt = 'consent', authorization_prompt_message = '')
                credentials = flow.credentials

                with open("token.pickle", "wb") as f:
                    pickle.dump(credentials, f)

        youtube = build('youtube', 'v3', credentials = credentials)

        return youtube