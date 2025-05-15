import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.auth.transport.requests
import google.oauth2.credentials
import isodate
import time
from itertools import islice

def chunker(iterable, size):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk

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

def get_all_liked_videos(youtube):
    videos = []
    next_page_token = None

    while True:
        request = youtube.videos().list(
            part="id,snippet",
            myRating="like",
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["id"]
            videos.append((title, video_id))

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos

def unlike_shorts_scaled(youtube, videos):
    # Process videos in batches of 50 for details API
    for batch in chunker(videos, 50):
        video_ids = [vid for _, vid in batch]

        response = youtube.videos().list(
            part="contentDetails",
            id=",".join(video_ids)
        ).execute()

        video_details = {item["id"]: item for item in response.get("items", [])}

        for title, vid in batch:
            item = video_details.get(vid)
            if not item:
                continue

            duration_iso = item["contentDetails"]["duration"]
            duration_sec = int(isodate.parse_duration(duration_iso).total_seconds())

            if duration_sec < 60:
                print(f"Unliking short video: {title} ({duration_sec}s)")
                try:
                    youtube.videos().rate(id=vid, rating="none").execute()
                    # Slight delay to be polite to API quota
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Error unliking {title}: {e}")

if __name__ == "__main__":
    youtube = get_authenticated_service()
    print("✅ Authenticated and connected to YouTube API")
    
    videos = get_all_liked_videos(youtube)
    print(f"Found {len(videos)} liked videos")

    unlike_shorts_scaled(youtube, videos)
