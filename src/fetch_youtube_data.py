from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)


def get_uploads_playlist_id(channel_id: str) -> str:
    request = youtube.channels().list(
        part="contentDetails,snippet",
        id=channel_id
    )
    response = request.execute()

    items = response.get("items", [])
    if not items:
        raise ValueError("Channel not found.")

    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_video_ids_from_playlist(playlist_id: str, max_videos: int = 20):
    video_ids = []
    next_page_token = None

    while len(video_ids) < max_videos:
        request = youtube.playlistItems().list(
            part="contentDetails,snippet",
            playlistId=playlist_id,
            maxResults=min(50, max_videos - len(video_ids)),
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            video_ids.append(video_id)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


def get_video_stats(video_ids):
    all_rows = []

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

            all_rows.append({
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

    return pd.DataFrame(all_rows)


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


def main():
    channel_id = input("Enter channel ID: ").strip()
    max_videos = int(input("Enter number of videos to fetch: ").strip())

    uploads_playlist_id = get_uploads_playlist_id(channel_id)
    video_ids = get_video_ids_from_playlist(uploads_playlist_id, max_videos=max_videos)

    videos_df = get_video_stats(video_ids)
    videos_output = r"E:\SMA Project\data\raw\api_videos.csv"
    videos_df.to_csv(videos_output, index=False)
    print(f"Saved video data to: {videos_output}")

    all_comments = []
    for vid in video_ids:
        try:
            comments_df = get_comments(vid, max_comments=50)
            all_comments.append(comments_df)
            print(f"Fetched comments for {vid}")
        except Exception as e:
            print(f"Could not fetch comments for {vid}: {e}")

    if all_comments:
        final_comments = pd.concat(all_comments, ignore_index=True)
        comments_output = r"E:\SMA Project\data\raw\api_comments.csv"
        final_comments.to_csv(comments_output, index=False)
        print(f"Saved comments data to: {comments_output}")
    else:
        print("No comments fetched.")

if __name__ == "__main__":
    main()