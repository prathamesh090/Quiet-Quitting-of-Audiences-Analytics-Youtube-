import os
import re
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from googleapiclient.discovery import build

# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="Quiet Quitting Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# Load Environment
# =========================================================
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# =========================================================
# Constants
# =========================================================
DATASET_SENTIMENT_PATH = r"E:\SMA Project\data\processed\comment_sentiment.csv"
DATASET_ENGAGEMENT_PATH = r"E:\SMA Project\data\processed\video_engagement.csv"
DATASET_REPORT_PATH = r"E:\SMA Project\data\processed\quiet_quitting_report.csv"

API_RAW_VIDEOS_PATH = r"E:\SMA Project\data\raw\api_videos.csv"
API_RAW_COMMENTS_PATH = r"E:\SMA Project\data\raw\api_comments.csv"

API_PROCESSED_VIDEOS_PATH = r"E:\SMA Project\data\processed\api_video_engagement.csv"
API_PROCESSED_COMMENTS_PATH = r"E:\SMA Project\data\processed\api_comment_sentiment.csv"
API_REPORT_PATH = r"E:\SMA Project\data\processed\api_quiet_quitting_report.csv"

DISENGAGEMENT_KEYWORDS = [
    "boring",
    "same",
    "repetitive",
    "too many ads",
    "ads",
    "ad",
    "changed",
    "not interesting",
    "miss old",
    "old content",
    "unsub",
    "unsubscribe",
    "stopped watching",
    "used to be better"
]

# =========================================================
# Styling
# =========================================================
st.markdown("""
<style>
    .main {
        background-color: #f8f9fb;
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 1rem;
        padding-left: 1.8rem;
        padding-right: 1.8rem;
    }
    .hero-box {
        background: linear-gradient(90deg, #111827, #1f2937);
        color: white;
        padding: 22px;
        border-radius: 16px;
        margin-bottom: 18px;
    }
    .hero-title {
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        font-size: 15px;
        color: #d1d5db;
    }
    .kpi-card {
        background-color: white;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        text-align: center;
        border: 1px solid #e6eaf0;
    }
    .kpi-title {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }
    .section-card {
        background-color: white;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #e6eaf0;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# YouTube API Helpers
# =========================================================
@st.cache_resource
def get_youtube_client():
    if not API_KEY:
        return None
    return build("youtube", "v3", developerKey=API_KEY)


def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_sentiment_score_simple(text):
    text = str(text).lower()

    positive_words = [
        "love", "great", "amazing", "awesome", "good", "nice", "best",
        "fun", "interesting", "excellent", "enjoy", "liked"
    ]
    negative_words = [
        "boring", "bad", "worst", "hate", "same", "repetitive", "ads",
        "annoying", "changed", "unsub", "unsubscribe", "not interesting"
    ]

    pos = sum(1 for word in positive_words if word in text)
    neg = sum(1 for word in negative_words if word in text)

    if pos > neg:
        return 0.5
    elif neg > pos:
        return -0.5
    return 0.0


def get_sentiment_label(score):
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"


def keyword_flag(text):
    text = str(text).lower()
    return 1 if any(word in text for word in DISENGAGEMENT_KEYWORDS) else 0


def find_channel_by_name(query, max_results=8):
    youtube = get_youtube_client()
    if youtube is None:
        return []

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
    youtube = get_youtube_client()
    if youtube is None:
        return None

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
    youtube = get_youtube_client()
    if youtube is None:
        return []

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
    youtube = get_youtube_client()
    if youtube is None:
        return pd.DataFrame()

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
    youtube = get_youtube_client()
    if youtube is None:
        return pd.DataFrame()

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


# =========================================================
# Processing Helpers
# =========================================================
def process_api_data(videos_df, comments_df):
    videos_df = videos_df.copy()
    comments_df = comments_df.copy()

    if videos_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    videos_df = videos_df.drop_duplicates().dropna(subset=["video_id", "title"])
    comments_df = comments_df.drop_duplicates()

    for col in ["views", "likes", "comment_total"]:
        if col in videos_df.columns:
            videos_df[col] = pd.to_numeric(videos_df[col], errors="coerce").fillna(0)

    for col in ["likes", "replies"]:
        if col in comments_df.columns:
            comments_df[col] = pd.to_numeric(comments_df[col], errors="coerce").fillna(0)

    videos_df["clean_title"] = videos_df["title"].apply(clean_text)
    videos_df["clean_tags"] = videos_df["tags"].apply(clean_text)
    videos_df["engagement_score"] = (
        (videos_df["likes"] + videos_df["comment_total"]) / videos_df["views"].replace(0, 1)
    ) * 100
    videos_df["like_view_ratio"] = (videos_df["likes"] / videos_df["views"].replace(0, 1)) * 100
    videos_df["comment_view_ratio"] = (videos_df["comment_total"] / videos_df["views"].replace(0, 1)) * 100

    if not comments_df.empty and "comment_text" in comments_df.columns:
        comments_df = comments_df.dropna(subset=["video_id", "comment_text"])
        comments_df["clean_comment"] = comments_df["comment_text"].apply(clean_text)
        comments_df = comments_df[comments_df["clean_comment"].str.strip() != ""]
        comments_df["sentiment_score"] = comments_df["clean_comment"].apply(get_sentiment_score_simple)
        comments_df["sentiment_label"] = comments_df["sentiment_score"].apply(get_sentiment_label)
        comments_df["disengagement_keyword_flag"] = comments_df["clean_comment"].apply(keyword_flag)
    else:
        comments_df = pd.DataFrame(columns=[
            "video_id", "comment_text", "clean_comment",
            "sentiment_score", "sentiment_label", "disengagement_keyword_flag"
        ])

    report_df = create_report(videos_df, comments_df)

    return videos_df, comments_df, report_df


def create_report(video_df, comment_df):
    if video_df.empty:
        return pd.DataFrame([{
            "positive_comment_ratio": 0.0,
            "neutral_comment_ratio": 0.0,
            "negative_comment_ratio": 0.0,
            "disengagement_keyword_ratio": 0.0,
            "average_engagement_score": 0.0,
            "low_engagement_video_ratio": 0.0,
            "repeated_title_ratio": 0.0,
            "quiet_quitting_risk_score": 0,
            "risk_label": "No Data"
        }])

    sentiment_dist = (
        comment_df["sentiment_label"].value_counts(normalize=True)
        if not comment_df.empty and "sentiment_label" in comment_df.columns
        else pd.Series(dtype=float)
    )

    positive_ratio = float(sentiment_dist.get("positive", 0))
    neutral_ratio = float(sentiment_dist.get("neutral", 0))
    negative_ratio = float(sentiment_dist.get("negative", 0))

    disengagement_keyword_ratio = (
        float(comment_df["disengagement_keyword_flag"].mean())
        if not comment_df.empty and "disengagement_keyword_flag" in comment_df.columns
        else 0.0
    )

    avg_engagement = float(video_df["engagement_score"].mean())
    low_engagement_ratio = float((video_df["engagement_score"] < avg_engagement).mean())

    repeated_title_ratio = (
        float(video_df["clean_title"].duplicated().mean())
        if "clean_title" in video_df.columns else 0.0
    )

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

    return pd.DataFrame([{
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


def load_dataset_files():
    sentiment_df = pd.read_csv(DATASET_SENTIMENT_PATH)
    engagement_df = pd.read_csv(DATASET_ENGAGEMENT_PATH)
    report_df = pd.read_csv(DATASET_REPORT_PATH)
    return engagement_df, sentiment_df, report_df


def save_api_outputs(videos_df, comments_df, report_df):
    os.makedirs(os.path.dirname(API_RAW_VIDEOS_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(API_PROCESSED_VIDEOS_PATH), exist_ok=True)

    videos_df.to_csv(API_RAW_VIDEOS_PATH, index=False)
    comments_df.to_csv(API_RAW_COMMENTS_PATH, index=False)
    videos_df.to_csv(API_PROCESSED_VIDEOS_PATH, index=False)
    comments_df.to_csv(API_PROCESSED_COMMENTS_PATH, index=False)
    report_df.to_csv(API_REPORT_PATH, index=False)


def calculate_metrics(video_df, comment_df):
    if video_df.empty:
        return {
            "risk_score": 0,
            "risk_label": "No Data",
            "avg_engagement": 0.0,
            "positive_ratio": 0.0,
            "negative_ratio": 0.0,
            "neutral_ratio": 0.0,
            "video_count": 0,
            "comment_count": 0,
            "keyword_ratio": 0.0
        }

    avg_engagement = float(video_df["engagement_score"].mean())

    if not comment_df.empty and "sentiment_label" in comment_df.columns:
        sentiment_dist = comment_df["sentiment_label"].value_counts(normalize=True)
        positive_ratio = float(sentiment_dist.get("positive", 0))
        neutral_ratio = float(sentiment_dist.get("neutral", 0))
        negative_ratio = float(sentiment_dist.get("negative", 0))
    else:
        positive_ratio = 0.0
        neutral_ratio = 0.0
        negative_ratio = 0.0

    repeated_title_ratio = (
        float(video_df["clean_title"].duplicated().mean())
        if "clean_title" in video_df.columns else 0.0
    )
    low_engagement_ratio = float((video_df["engagement_score"] < avg_engagement).mean())
    keyword_ratio = (
        float(comment_df["clean_comment"].apply(keyword_flag).mean())
        if not comment_df.empty and "clean_comment" in comment_df.columns else 0.0
    )

    risk_score = 0
    if negative_ratio > 0.25:
        risk_score += 30
    if keyword_ratio > 0.05:
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

    return {
        "risk_score": risk_score,
        "risk_label": risk_label,
        "avg_engagement": avg_engagement,
        "positive_ratio": positive_ratio,
        "negative_ratio": negative_ratio,
        "neutral_ratio": neutral_ratio,
        "video_count": len(video_df),
        "comment_count": len(comment_df),
        "keyword_ratio": keyword_ratio
    }


# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("Controls")

data_source = st.sidebar.radio(
    "Select Data Source",
    ["Dataset", "Live API Data"]
)

channel_input = None
max_videos = 5
selected_channel_id = None
selected_channel_title = None
analyze_api = False

if data_source == "Live API Data":
    st.sidebar.subheader("Live Creator Analysis")

    if not API_KEY:
        st.sidebar.error("YOUTUBE_API_KEY not found in .env file")

    channel_input = st.sidebar.text_input("Search channel name")
    max_videos = st.sidebar.slider("Number of videos to fetch", 3, 20, 5)

    if st.sidebar.button("Search Channels"):
        if channel_input.strip():
            matches = find_channel_by_name(channel_input.strip(), max_results=8)
            st.session_state["channel_matches"] = matches
        else:
            st.sidebar.warning("Please enter a channel name.")

    if "channel_matches" in st.session_state and st.session_state["channel_matches"]:
        channel_options = {
            f"{item['channel_title']} ({item['channel_id']})": item
            for item in st.session_state["channel_matches"]
        }

        selected_option = st.sidebar.selectbox(
            "Select the correct channel",
            list(channel_options.keys())
        )

        selected_channel = channel_options[selected_option]
        selected_channel_id = selected_channel["channel_id"]
        selected_channel_title = selected_channel["channel_title"]

        st.sidebar.caption(f"Selected: {selected_channel_title}")

        with st.sidebar.expander("Matching channels"):
            for item in st.session_state["channel_matches"]:
                st.write(f"**{item['channel_title']}**")
                st.caption(item["channel_id"])
                if item["description"]:
                    st.caption(item["description"][:120])

        analyze_api = st.sidebar.button("Analyze Selected Channel")

# =========================================================
# API Fetch + Process
# =========================================================
if data_source == "Live API Data" and analyze_api:
    try:
        playlist_id = get_uploads_playlist_id(selected_channel_id)

        if not playlist_id:
            st.sidebar.error("Could not fetch uploads playlist for this channel.")
            st.stop()

        with st.spinner("Fetching videos and comments..."):
            video_ids = get_video_ids_from_playlist(playlist_id, max_videos=max_videos)
            raw_videos_df = get_video_stats(video_ids)

            all_comments = []
            for vid in video_ids:
                try:
                    cdf = get_comments(vid, max_comments=50)
                    all_comments.append(cdf)
                except Exception:
                    pass

            raw_comments_df = pd.concat(all_comments, ignore_index=True) if all_comments else pd.DataFrame()

            processed_videos_df, processed_comments_df, report_df = process_api_data(
                raw_videos_df, raw_comments_df
            )

            save_api_outputs(processed_videos_df, processed_comments_df, report_df)

            st.session_state["api_videos_df"] = processed_videos_df
            st.session_state["api_comments_df"] = processed_comments_df
            st.session_state["api_report_df"] = report_df
            st.session_state["active_channel_title"] = selected_channel_title
            st.session_state["active_channel_id"] = selected_channel_id

        st.sidebar.success(f"Analysis completed for {selected_channel_title}")

    except Exception as e:
        st.sidebar.error(f"API fetch failed: {e}")
        st.stop()

# =========================================================
# Load Data
# =========================================================
if data_source == "Dataset":
    engagement_df, sentiment_df, report_df = load_dataset_files()
    channel_label = "Historical Dataset"
else:
    if "api_videos_df" in st.session_state:
        engagement_df = st.session_state["api_videos_df"].copy()
        sentiment_df = st.session_state["api_comments_df"].copy()
        report_df = st.session_state["api_report_df"].copy()
        channel_label = st.session_state.get("active_channel_title", "Selected Channel")
    else:
        st.markdown("""
            <div class="hero-box">
                <div class="hero-title">Quiet Quitting of Audiences Dashboard</div>
                <div class="hero-subtitle">
                    Select Live API Data, search a channel, choose the correct match, and click Analyze Selected Channel.
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.info("No live channel analyzed yet.")
        st.stop()

# =========================================================
# Filter Controls
# =========================================================
top_n = st.sidebar.slider("Top videos to display", 5, 20, 10)

min_views = int(engagement_df["views"].min()) if not engagement_df.empty else 0
max_views = int(engagement_df["views"].max()) if not engagement_df.empty else 1

selected_view_range = st.sidebar.slider(
    "View range",
    min_value=min_views,
    max_value=max_views if max_views > min_views else min_views + 1,
    value=(min_views, max_views if max_views > min_views else min_views + 1)
)

if "category_name" in engagement_df.columns:
    categories = ["All"] + sorted([str(x) for x in engagement_df["category_name"].dropna().unique()])
else:
    categories = ["All"]

selected_category = st.sidebar.selectbox("Category", categories)

# =========================================================
# Apply Filters
# =========================================================
filtered_videos = engagement_df[
    (engagement_df["views"] >= selected_view_range[0]) &
    (engagement_df["views"] <= selected_view_range[1])
].copy()

if selected_category != "All" and "category_name" in filtered_videos.columns:
    filtered_videos = filtered_videos[filtered_videos["category_name"] == selected_category]

if "video_id" in filtered_videos.columns and "video_id" in sentiment_df.columns:
    selected_video_ids = filtered_videos["video_id"].dropna().unique()
    filtered_comments = sentiment_df[sentiment_df["video_id"].isin(selected_video_ids)].copy()
else:
    filtered_comments = sentiment_df.copy()

metrics = calculate_metrics(filtered_videos, filtered_comments)

# =========================================================
# Header
# =========================================================
st.markdown(f"""
    <div class="hero-box">
        <div class="hero-title">Quiet Quitting of Audiences Dashboard</div>
        <div class="hero-subtitle">
            Source: {data_source} | Channel: {channel_label}
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# KPI Cards
# =========================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Risk Score</div>
            <div class="kpi-value">{metrics['risk_score']}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Risk Level</div>
            <div class="kpi-value">{metrics['risk_label']}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Engagement</div>
            <div class="kpi-value">{metrics['avg_engagement']:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Videos Selected</div>
            <div class="kpi-value">{metrics['video_count']}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")

if metrics["risk_label"] == "High":
    st.error("High silent disengagement risk detected for the selected audience data.")
elif metrics["risk_label"] == "Medium":
    st.warning("Moderate silent disengagement risk detected for the selected audience data.")
elif metrics["risk_label"] == "Low":
    st.success("Low silent disengagement risk detected for the selected audience data.")
else:
    st.info("No matching data found for the selected filters.")

# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Audience Sentiment",
    "Video Engagement",
    "Recommendations"
])

# =========================================================
# Tab 1: Overview
# =========================================================
with tab1:
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Project Summary")

        summary_df = pd.DataFrame({
            "Metric": [
                "Risk Score",
                "Risk Level",
                "Average Engagement",
                "Positive Comment Ratio",
                "Neutral Comment Ratio",
                "Negative Comment Ratio",
                "Disengagement Keyword Ratio",
                "Selected Videos",
                "Selected Comments"
            ],
            "Value": [
                metrics["risk_score"],
                metrics["risk_label"],
                round(metrics["avg_engagement"], 2),
                f"{metrics['positive_ratio']:.2%}",
                f"{metrics['neutral_ratio']:.2%}",
                f"{metrics['negative_ratio']:.2%}",
                f"{metrics['keyword_ratio']:.2%}",
                metrics["video_count"],
                metrics["comment_count"]
            ]
        })

        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Comment Sentiment Split")

        sentiment_chart_df = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Ratio": [
                metrics["positive_ratio"],
                metrics["neutral_ratio"],
                metrics["negative_ratio"]
            ]
        })

        fig_pie = px.pie(
            sentiment_chart_df,
            names="Sentiment",
            values="Ratio",
            hole=0.45
        )
        fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Tab 2: Audience Sentiment
# =========================================================
with tab2:
    if filtered_comments.empty:
        st.warning("No comments available for the selected filters.")
    else:
        left, right = st.columns([1, 1])

        with left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Sentiment Count")

            sentiment_counts = filtered_comments["sentiment_label"].value_counts().reset_index()
            sentiment_counts.columns = ["Sentiment", "Count"]

            fig_bar = px.bar(
                sentiment_counts,
                x="Sentiment",
                y="Count",
                text="Count"
            )
            fig_bar.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Sample Negative Comments")

            show_cols = [c for c in ["comment_text", "sentiment_score"] if c in filtered_comments.columns]
            negative_comments = filtered_comments[
                filtered_comments["sentiment_label"] == "negative"
            ][show_cols].head(8)

            if negative_comments.empty:
                st.info("No negative comments found for the selected filters.")
            else:
                st.dataframe(negative_comments, use_container_width=True, hide_index=True)

            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Tab 3: Video Engagement
# =========================================================
with tab3:
    if filtered_videos.empty:
        st.warning("No videos available for the selected filters.")
    else:
        top_videos = filtered_videos.sort_values(
            by="engagement_score",
            ascending=False
        ).head(top_n)

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader(f"Top {top_n} Videos by Engagement")

            fig_top = px.bar(
                top_videos,
                x="engagement_score",
                y="title",
                orientation="h",
                hover_data=[c for c in ["views", "likes", "comment_total"] if c in top_videos.columns]
            )
            fig_top.update_layout(
                yaxis={"categoryorder": "total ascending"},
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_top, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Engagement Distribution")

            fig_hist = px.histogram(
                filtered_videos,
                x="engagement_score",
                nbins=25
            )
            fig_hist.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_hist, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("")

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Video Performance Table")

        show_cols = [
            "title",
            "channel_title",
            "category_name",
            "published_at",
            "views",
            "likes",
            "comment_total",
            "engagement_score"
        ]
        show_cols = [c for c in show_cols if c in filtered_videos.columns]

        st.dataframe(
            filtered_videos[show_cols]
            .sort_values(by="engagement_score", ascending=False)
            .head(20),
            use_container_width=True,
            hide_index=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Tab 4: Recommendations
# =========================================================
with tab4:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Final Recommendation")

    if metrics["risk_label"] == "High":
        st.write("""
        - Reduce repetitive content and refresh content themes.
        - Review negative audience comments carefully.
        - Avoid excessive promotional or ad-heavy posting.
        - Improve interaction through questions, polls, and replies.
        - Monitor engagement regularly to detect silent disengagement early.
        """)
    elif metrics["risk_label"] == "Medium":
        st.write("""
        - Monitor engagement decline in underperforming content categories.
        - Experiment with new content formats.
        - Review audience feedback and improve engagement quality.
        - Track changes in comment sentiment over time.
        """)
    elif metrics["risk_label"] == "Low":
        st.write("""
        - Maintain the current content strategy.
        - Continue regular sentiment and engagement monitoring.
        - Preserve high-performing themes and audience interaction patterns.
        """)
    else:
        st.write("Adjust filters to display relevant audience data.")

    st.markdown("</div>", unsafe_allow_html=True)