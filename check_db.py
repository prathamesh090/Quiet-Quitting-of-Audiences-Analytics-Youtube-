import pandas as pd
import json

video_path = r"E:\SMA Project\data\raw\USvideos.csv"
comment_path = r"E:\SMA Project\data\raw\UScomments.csv"
category_path = r"E:\SMA Project\data\raw\US_category_id.json"

videos_df = pd.read_csv(
    video_path,
    engine="python",
    on_bad_lines="skip"
)

comments_df = pd.read_csv(
    comment_path,
    engine="python",
    on_bad_lines="skip"
)

print("USvideos columns:")
print(videos_df.columns.tolist())
print("\nUSvideos sample:")
print(videos_df.head())
print("\nUSvideos shape:")
print(videos_df.shape)

print("\n" + "=" * 80 + "\n")

print("UScomments columns:")
print(comments_df.columns.tolist())
print("\nUScomments sample:")
print(comments_df.head())
print("\nUScomments shape:")
print(comments_df.shape)

print("\n" + "=" * 80 + "\n")

with open(category_path, "r", encoding="utf-8") as f:
    category_data = json.load(f)

print("US category JSON loaded successfully")
print("Top-level keys:", category_data.keys())
print("First category item:")
print(category_data["items"][0])