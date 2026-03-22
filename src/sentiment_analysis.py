import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# =========================================
# Select source: "dataset", "api", or "both"
# =========================================
data_source = "both"

# =========================================
# File paths
# =========================================
dataset_input_path = r"E:\SMA Project\data\processed\clean_comments.csv"
dataset_output_path = r"E:\SMA Project\data\processed\comment_sentiment.csv"

api_input_path = r"E:\SMA Project\data\processed\api_clean_comments.csv"
api_output_path = r"E:\SMA Project\data\processed\api_comment_sentiment.csv"

analyzer = SentimentIntensityAnalyzer()


def get_sentiment_score(text):
    return analyzer.polarity_scores(str(text))["compound"]


def get_sentiment_label(score):
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"


def run_sentiment_analysis(input_path, output_path, label):
    df = pd.read_csv(input_path)

    df["sentiment_score"] = df["clean_comment"].apply(get_sentiment_score)
    df["sentiment_label"] = df["sentiment_score"].apply(get_sentiment_label)

    df.to_csv(output_path, index=False)

    print(f"{label} sentiment file saved to: {output_path}")
    print(df["sentiment_label"].value_counts())
    print("-" * 60)


if __name__ == "__main__":
    if data_source == "dataset":
        run_sentiment_analysis(dataset_input_path, dataset_output_path, "Dataset")

    elif data_source == "api":
        run_sentiment_analysis(api_input_path, api_output_path, "API")

    elif data_source == "both":
        run_sentiment_analysis(dataset_input_path, dataset_output_path, "Dataset")
        run_sentiment_analysis(api_input_path, api_output_path, "API")

    else:
        print("Invalid data_source. Use 'dataset', 'api', or 'both'.")