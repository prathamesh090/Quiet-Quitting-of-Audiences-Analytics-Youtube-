import pandas as pd

video_path = r"E:\SMA Project\data\raw\api_videos.csv"
comment_path = r"E:\SMA Project\data\raw\api_comments.csv"

videos_df = pd.read_csv(video_path)
comments_df = pd.read_csv(comment_path)

print("API VIDEOS")
print(videos_df.head())
print("\nColumns:", videos_df.columns.tolist())
print("Shape:", videos_df.shape)

print("\n" + "="*60 + "\n")

print("API COMMENTS")
print(comments_df.head())
print("\nColumns:", comments_df.columns.tolist())
print("Shape:", comments_df.shape)