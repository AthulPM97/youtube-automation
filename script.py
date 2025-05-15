import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.auth.transport.requests
import google.oauth2.credentials

# Define the required OAuth scope
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    creds = None
    if os.path.exists("token.json"):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file("token.json", scopes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes)
            creds = flow.run_local_server(port=8080, open_browser=False)
        
        # Save the credentials for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def get_liked_videos(youtube):
    request = youtube.videos().list(
        part="id,snippet",
        myRating="like",
        maxResults=50
    )
    response = request.execute()

    videos = []
    for item in response.get("items", []):
        title = item["snippet"]["title"]
        video_id = item["id"]
        videos.append((title, video_id))
    
    return videos

# Example usage
if __name__ == "__main__":
    youtube = get_authenticated_service()
    print("✅ Authenticated and connected to YouTube API")
    videos = get_liked_videos(youtube)
    for title, vid in videos:
        print(f"{title} - https://youtu.be/{vid}")

