from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)


def find_channel_by_name(query, max_results=8):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="channel",
        maxResults=max_results
    )
    response = request.execute()

    channels = []
    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        channels.append({
            "channel_title": snippet.get("title", ""),
            "channel_id": snippet.get("channelId", ""),
            "description": snippet.get("description", "")
        })

    return channels


def get_uploads_playlist_id(channel_id):
    request = youtube.channels().list(
        part="contentDetails,snippet",
        id=channel_id
    )
    response = request.execute()

    items = response.get("items", [])
    if not items:
        return None

    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_video_ids_from_playlist(playlist_id, max_videos=10):
    video_ids = []
    next_page_token = None

    while len(video_ids) < max_videos:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=min(50, max_videos - len(video_ids)),
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


def get_video_stats(video_ids):
    rows = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch)
        )
        response = request.execute()

        for item in response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})

            rows.append({
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "category_id": snippet.get("categoryId", ""),
                "tags": " | ".join(snippet.get("tags", [])) if "tags" in snippet else "",
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comment_total": int(stats.get("commentCount", 0))
            })

    return pd.DataFrame(rows)


def get_comments(video_id, max_comments=50):
    rows = []
    next_page_token = None

    while len(rows) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments - len(rows)),
            pageToken=next_page_token,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            rows.append({
                "video_id": video_id,
                "comment_text": comment.get("textDisplay", ""),
                "likes": int(comment.get("likeCount", 0)),
                "replies": int(item["snippet"].get("totalReplyCount", 0)),
                "comment_published_at": comment.get("publishedAt", "")
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return pd.DataFrame(rows)