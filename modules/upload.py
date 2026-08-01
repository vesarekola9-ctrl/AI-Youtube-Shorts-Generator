import os
import json
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

class YouTubeUploader:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        self.API_SERVICE_NAME = "youtube"
        self.API_VERSION = "v3"
        self.CLIENT_SECRETS_FILE = "client_secret.json"
        self.TOKEN_FILE = "token.json"

    def _setup_files(self):
        # 1. Luodaan client_secret.json lennosta
        if not os.path.exists(self.CLIENT_SECRETS_FILE):
            secret_content = os.getenv("YOUTUBE_CLIENT_SECRET_JSON")
            if secret_content:
                with open(self.CLIENT_SECRETS_FILE, "w") as f:
                    f.write(secret_content)
                print("⚙️ Luotu client_secret.json ympäristömuuttujasta.")
            else:
                print("⚠️ Varoitus: Ympäristömuuttujaa YOUTUBE_CLIENT_SECRET_JSON ei löytynyt.")

        # 2. Luodaan token.json lennosta (jos sellainen on tallennettu GitHub Secretsiin)
        if not os.path.exists(self.TOKEN_FILE):
            token_content = os.getenv("YOUTUBE_TOKEN_JSON")
            if token_content:
                with open(self.TOKEN_FILE, "w") as f:
                    f.write(token_content)
                print("⚙️ Luotu token.json ympäristömuuttujasta.")

    def upload_short(self, video_path, title="Automated YouTube Short #Shorts", description="Generated automatically with AI AutoShorts 🚀"):
        if not os.path.exists(video_path):
            print(f"❌ Upload Error: Video file not found at {video_path}")
            return

        self._setup_files()

        if not os.path.exists(self.CLIENT_SECRETS_FILE):
            print(f"❌ Upload Error: Missing '{self.CLIENT_SECRETS_FILE}'!")
            return

        print("🚀 Starting YouTube Upload process...")

        try:
            credentials = None
            
            # Yritetään ladata aiemmin tallennettu token
            if os.path.exists(self.TOKEN_FILE):
                credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(
                    self.TOKEN_FILE, self.SCOPES
                )

            # Jos tokeneita ei ole tai ne ovat vanhentuneita/virheellisiä
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(google.auth.transport.requests.Request())
                else:
                    # Jos ajetaan paikallisesti koneella, voidaan käyttää selainta
                    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        self.CLIENT_SECRETS_FILE, self.SCOPES
                    )
                    credentials = flow.run_local_server(port=0)
                
                # Tallennetaan token paikallisesti uusiokäyttöä varten
                with open(self.TOKEN_FILE, "w") as token:
                    token.write(credentials.to_json())

            youtube = googleapiclient.discovery.build(
                self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials
            )

            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["shorts", "ai", "automation", "viral"],
                    "categoryId": "24"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }

            media = googleapiclient.http.MediaFileUpload(
                video_path, chunksize=-1, resumable=True, mimetype="video/mp4"
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"   📥 Upload progress: {int(status.progress() * 100)}%")

            print(f"✅ Video successfully uploaded! Video ID: {response.get('id')}")
            print(f"🔗 Linkki: https://youtu.be/{response.get('id')}")

        except Exception as e:
            print(f"❌ YouTube Upload Failed: {e}")

if __name__ == "__main__":
    uploader = YouTubeUploader()
    uploader.upload_short("assets/final/final_short.mp4")