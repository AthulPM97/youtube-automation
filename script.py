import google_auth_oauthlib.flow
import googleapiclient.discovery

# Define the required OAuth scope
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "credentials.json", scopes)

    # Prevent it from auto-opening browser (manual copy-paste instead)
    credentials = flow.run_local_server(port=8080, open_browser=False)
    
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

# Example usage
if __name__ == "__main__":
    youtube = get_authenticated_service()
    print("✅ Authenticated and connected to YouTube API")
