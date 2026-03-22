from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)

request = youtube.channels().list(
    part="snippet",
    id="UC_x5XG1OV2P6uZZ5FSM9Ttw"  # Google Developers channel
)

response = request.execute()

print("API is working.")
print(response)