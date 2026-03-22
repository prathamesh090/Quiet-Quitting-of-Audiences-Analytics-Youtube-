from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)

def find_channel(query):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="channel",
        maxResults=5
    )
    response = request.execute()

    for i, item in enumerate(response.get("items", []), start=1):
        print(f"{i}. {item['snippet']['title']} | {item['snippet']['channelId']}")

if __name__ == "__main__":
    query = input("Enter channel name: ")
    find_channel(query)