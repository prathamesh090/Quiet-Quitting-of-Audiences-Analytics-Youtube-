import pandas as pd

# =========================================
# Select source: "dataset", "api", or "both"
# =========================================
data_source = "both"

# =========================================
# File paths
# =========================================
dataset_input_path = r"E:\SMA Project\data\processed\clean_videos.csv"
dataset_output_path = r"E:\SMA Project\data\processed\video_engagement.csv"

api_input_path = r"E:\SMA Project\data\processed\api_clean_videos.csv"
api_output_path = r"E:\SMA Project\data\processed\api_video_engagement.csv"


def run_engagement_analysis(input_path, output_path, label):
    df = pd.read_csv(input_path)

    # Safe numeric conversion
    for col in ["views", "likes", "dislikes", "comment_total"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Engagement score
    df["engagement_score"] = (
        (df["likes"] + df["comment_total"]) / df["views"].replace(0, 1)
    ) * 100

    # Ratios
    df["like_view_ratio"] = (df["likes"] / df["views"].replace(0, 1)) * 100
    df["comment_view_ratio"] = (df["comment_total"] / df["views"].replace(0, 1)) * 100

    # Sort by views
    df = df.sort_values(by="views", ascending=False)

    df.to_csv(output_path, index=False)

    print(f"{label} engagement file saved to: {output_path}")
    print(df[["title", "views", "likes", "comment_total", "engagement_score"]].head(5))
    print("-" * 60)


if __name__ == "__main__":
    if data_source == "dataset":
        run_engagement_analysis(dataset_input_path, dataset_output_path, "Dataset")

    elif data_source == "api":
        run_engagement_analysis(api_input_path, api_output_path, "API")

    elif data_source == "both":
        run_engagement_analysis(dataset_input_path, dataset_output_path, "Dataset")
        run_engagement_analysis(api_input_path, api_output_path, "API")

    else:
        print("Invalid data_source. Use 'dataset', 'api', or 'both'.")