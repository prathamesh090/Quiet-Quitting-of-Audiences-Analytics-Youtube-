import pandas as pd

# =========================================
# Select source: "dataset", "api", or "both"
# =========================================
data_source = "both"

# =========================================
# File paths
# =========================================
dataset_video_path = r"E:\SMA Project\data\processed\video_engagement.csv"
dataset_comment_path = r"E:\SMA Project\data\processed\comment_sentiment.csv"
dataset_output_path = r"E:\SMA Project\data\processed\quiet_quitting_report.csv"

api_video_path = r"E:\SMA Project\data\processed\api_video_engagement.csv"
api_comment_path = r"E:\SMA Project\data\processed\api_comment_sentiment.csv"
api_output_path = r"E:\SMA Project\data\processed\api_quiet_quitting_report.csv"

DISENGAGEMENT_KEYWORDS = [
    "boring",
    "same",
    "repetitive",
    "ads",
    "ad",
    "changed",
    "not interesting",
    "miss old",
    "old content",
    "unsub",
    "unsubscribe"
]


def keyword_flag(text):
    text = str(text).lower()
    for word in DISENGAGEMENT_KEYWORDS:
        if word in text:
            return 1
    return 0


def run_quiet_quitting_detection(video_path, comment_path, output_path, label):
    video_df = pd.read_csv(video_path)
    comment_df = pd.read_csv(comment_path)

    negative_ratio = (
        comment_df["sentiment_label"].value_counts(normalize=True).get("negative", 0)
    )
    positive_ratio = (
        comment_df["sentiment_label"].value_counts(normalize=True).get("positive", 0)
    )
    neutral_ratio = (
        comment_df["sentiment_label"].value_counts(normalize=True).get("neutral", 0)
    )

    comment_df["disengagement_keyword_flag"] = comment_df["clean_comment"].apply(keyword_flag)
    disengagement_keyword_ratio = comment_df["disengagement_keyword_flag"].mean()

    avg_engagement = video_df["engagement_score"].mean()
    low_engagement_ratio = (video_df["engagement_score"] < avg_engagement).mean()

    repeated_title_ratio = 0
    if "clean_title" in video_df.columns:
        repeated_title_ratio = video_df["clean_title"].duplicated().mean()

    risk_score = 0

    if negative_ratio > 0.25:
        risk_score += 30
    if disengagement_keyword_ratio > 0.05:
        risk_score += 25
    if low_engagement_ratio > 0.60:
        risk_score += 25
    if repeated_title_ratio > 0.10:
        risk_score += 20

    if risk_score <= 30:
        risk_label = "Low"
    elif risk_score <= 60:
        risk_label = "Medium"
    else:
        risk_label = "High"

    report = pd.DataFrame([{
        "positive_comment_ratio": round(positive_ratio, 4),
        "neutral_comment_ratio": round(neutral_ratio, 4),
        "negative_comment_ratio": round(negative_ratio, 4),
        "disengagement_keyword_ratio": round(disengagement_keyword_ratio, 4),
        "average_engagement_score": round(avg_engagement, 4),
        "low_engagement_video_ratio": round(low_engagement_ratio, 4),
        "repeated_title_ratio": round(repeated_title_ratio, 4),
        "quiet_quitting_risk_score": risk_score,
        "risk_label": risk_label
    }])

    report.to_csv(output_path, index=False)

    print(f"{label} quiet quitting report saved to: {output_path}")
    print(report)
    print("-" * 60)


if __name__ == "__main__":
    if data_source == "dataset":
        run_quiet_quitting_detection(
            dataset_video_path,
            dataset_comment_path,
            dataset_output_path,
            "Dataset"
        )

    elif data_source == "api":
        run_quiet_quitting_detection(
            api_video_path,
            api_comment_path,
            api_output_path,
            "API"
        )

    elif data_source == "both":
        run_quiet_quitting_detection(
            dataset_video_path,
            dataset_comment_path,
            dataset_output_path,
            "Dataset"
        )
        run_quiet_quitting_detection(
            api_video_path,
            api_comment_path,
            api_output_path,
            "API"
        )

    else:
        print("Invalid data_source. Use 'dataset', 'api', or 'both'.")