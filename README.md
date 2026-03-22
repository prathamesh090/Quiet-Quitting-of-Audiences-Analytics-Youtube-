🚨 Quiet Quitting of Audiences
Detecting Silent Disengagement in Social Media

🚨 Follower count ≠ Active audience — this project reveals the hidden truth.

🔍 Overview

This project analyzes how audiences silently disengage from social media creators without unfollowing — a phenomenon known as “Quiet Quitting of Audiences.”

Instead of relying only on follower count, this system detects:

declining engagement
negative sentiment trends
repetitive content patterns
hidden audience dissatisfaction
🎯 Objective

To develop a Social Media Analytics System that:

identifies early signs of audience disengagement
converts raw social media data into actionable insights
helps creators and brands make better decisions
⚙️ Key Features
📊 Engagement Analysis
Engagement score calculation
Like/View ratio
Comment/View ratio
💬 Sentiment Analysis
Classifies comments into:
Positive
Neutral
Negative
⚠️ Quiet Quitting Detection
Custom risk scoring model:
Low
Medium
High
🔎 Keyword-Based Disengagement Detection

Detects phrases like:

“boring”
“same content”
“too many ads”
“not interesting”
🌐 Live YouTube API Integration
Search channels even with incorrect spelling
Suggest closest matching channels
Select correct channel before analysis
Fetch real-time:
videos
comments
Perform live audience analysis
📈 Interactive Dashboard (Streamlit)
Dataset vs Live API toggle
Channel search + suggestion system
Filters:
view range
category
top videos
Visualizations:
sentiment distribution
engagement charts
performance tables
Risk indicator (Low / Medium / High)
🧠 Core Concept

Many followers don’t unfollow — they simply stop engaging.

This project detects:

passive followers
declining interest
hidden churn
🏗️ System Pipeline
Data Collection (Dataset + YouTube API)
Data Cleaning & Preprocessing
Sentiment Analysis
Engagement Analysis
Quiet Quitting Detection
Dashboard Visualization
🛠️ Tech Stack
Python
Pandas, NumPy
Streamlit (Dashboard)
Plotly (Visualization)
YouTube Data API
Regex & NLP Techniques
📂 Project Structure
SMA Project/
│
├── dashboard/
│   └── app.py
│
├── src/
│   ├── clean_data.py
│   ├── sentiment_analysis.py
│   ├── engagement_analysis.py
│   ├── quiet_quitting_detector.py
│   └── youtube_api_utils.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── main.py
├── requirements.txt
└── README.md
🚀 How to Run
1. Install dependencies
pip install -r requirements.txt
2. Add YouTube API Key

Create .env file:

YOUTUBE_API_KEY=your_api_key_here
3. Run Dashboard
streamlit run dashboard/app.py
📊 Output

The system generates:

Engagement metrics
Sentiment distribution
Disengagement keyword analysis
Quiet quitting risk score
💡 Use Cases
Creator performance monitoring
Brand collaboration validation
Social media strategy optimization
Audience behavior research
⚠️ Important Notes
.env file is not included for security
API keys must not be shared publicly
Generated API CSV files are ignored in Git
