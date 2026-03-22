import pandas as pd
import re
import json

# =========================================
# Select source: "dataset", "api", or "both"
# =========================================
data_source = "both"

# =========================================
# Dataset file paths
# =========================================
video_path = r"E:\SMA Project\data\raw\USvideos.csv"
comment_path = r"E:\SMA Project\data\raw\UScomments.csv"
category_path = r"E:\SMA Project\data\raw\US_category_id.json"

clean_video_output = r"E:\SMA Project\data\processed\clean_videos.csv"
clean_comment_output = r"E:\SMA Project\data\processed\clean_comments.csv"

# =========================================
# API file paths
# =========================================
api_video_path = r"E:\SMA Project\data\raw\api_videos.csv"
api_comment_path = r"E:\SMA Project\data\raw\api_comments.csv"

api_video_output = r"E:\SMA Project\data\processed\api_clean_videos.csv"
api_comment_output = r"E:\SMA Project\data\processed\api_clean_comments.csv"


def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_category_map(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    category_map = {}
    for item in data["items"]:
        category_map[item["id"]] = item["snippet"]["title"]

    return category_map


def clean_dataset_videos():
    videos_df = pd.read_csv(video_path, engine="python", on_bad_lines="skip")

    videos_df = videos_df.drop_duplicates()
    videos_df = videos_df.dropna(subset=["video_id", "title"])

    numeric_cols = ["views", "likes", "dislikes", "comment_total"]
    for col in numeric_cols:
        videos_df[col] = pd.to_numeric(videos_df[col], errors="coerce").fillna(0)

    videos_df["clean_title"] = videos_df["title"].apply(clean_text)
    videos_df["clean_tags"] = videos_df["tags"].apply(clean_text)

    category_map = load_category_map(category_path)
    videos_df["category_id"] = videos_df["category_id"].astype(str)
    videos_df["category_name"] = videos_df["category_id"].map(category_map)

    videos_df.to_csv(clean_video_output, index=False)
    print("Clean dataset videos saved to:", clean_video_output)
    print("Shape:", videos_df.shape)


def clean_dataset_comments():
    comments_df = pd.read_csv(comment_path, engine="python", on_bad_lines="skip")

    comments_df = comments_df.drop_duplicates()
    comments_df = comments_df.dropna(subset=["video_id", "comment_text"])

    comments_df["likes"] = pd.to_numeric(comments_df["likes"], errors="coerce").fillna(0)
    comments_df["replies"] = pd.to_numeric(comments_df["replies"], errors="coerce").fillna(0)

    comments_df["clean_comment"] = comments_df["comment_text"].apply(clean_text)
    comments_df = comments_df[comments_df["clean_comment"].str.strip() != ""]

    comments_df.to_csv(clean_comment_output, index=False)
    print("Clean dataset comments saved to:", clean_comment_output)
    print("Shape:", comments_df.shape)


def clean_api_videos():
    videos_df = pd.read_csv(api_video_path)

    videos_df = videos_df.drop_duplicates()
    videos_df = videos_df.dropna(subset=["video_id", "title"])

    for col in ["views", "likes", "comment_total"]:
        videos_df[col] = pd.to_numeric(videos_df[col], errors="coerce").fillna(0)

    videos_df["clean_title"] = videos_df["title"].apply(clean_text)
    videos_df["clean_tags"] = videos_df["tags"].apply(clean_text)

    videos_df.to_csv(api_video_output, index=False)
    print("Clean API videos saved to:", api_video_output)
    print("Shape:", videos_df.shape)


def clean_api_comments():
    comments_df = pd.read_csv(api_comment_path)

    comments_df = comments_df.drop_duplicates()
    comments_df = comments_df.dropna(subset=["video_id", "comment_text"])

    for col in ["likes", "replies"]:
        if col in comments_df.columns:
            comments_df[col] = pd.to_numeric(comments_df[col], errors="coerce").fillna(0)

    comments_df["clean_comment"] = comments_df["comment_text"].apply(clean_text)
    comments_df = comments_df[comments_df["clean_comment"].str.strip() != ""]

    comments_df.to_csv(api_comment_output, index=False)
    print("Clean API comments saved to:", api_comment_output)
    print("Shape:", comments_df.shape)


if __name__ == "__main__":
    if data_source == "dataset":
        clean_dataset_videos()
        clean_dataset_comments()

    elif data_source == "api":
        clean_api_videos()
        clean_api_comments()

    elif data_source == "both":
        clean_dataset_videos()
        clean_dataset_comments()
        clean_api_videos()
        clean_api_comments()

    else:
        print("Invalid data_source. Use 'dataset', 'api', or 'both'.")