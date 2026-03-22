# 🚨 Quiet Quitting of Audiences  
### Detecting Silent Disengagement in Social Media

> 🚨 *Follower count ≠ Active audience — this project reveals the hidden truth.*

---

## 🔍 Overview

This project analyzes how audiences **silently disengage** from social media creators without unfollowing — a phenomenon known as **“Quiet Quitting of Audiences.”**

Instead of relying only on follower count, this system detects:
- declining engagement  
- negative sentiment trends  
- repetitive content patterns  
- hidden audience dissatisfaction  

---

## 🎯 Objective

To develop a **Social Media Analytics System** that:
- identifies early signs of audience disengagement  
- converts raw social media data into actionable insights  
- helps creators and brands make better decisions  

---

## ⚙️ Key Features

### 📊 Engagement Analysis
- Engagement score calculation  
- Like/View ratio  
- Comment/View ratio  

### 💬 Sentiment Analysis
- Classifies comments into:
  - Positive  
  - Neutral  
  - Negative  

### ⚠️ Quiet Quitting Detection
- Custom **risk scoring model**:
  - Low  
  - Medium  
  - High  

### 🔎 Keyword-Based Disengagement Detection
Detects phrases like:
- “boring”
- “same content”
- “too many ads”
- “not interesting”

---

## 🌐 Live YouTube API Integration

- Search channels even with **incorrect spelling**
- Suggest **closest matching channels**
- Select correct channel before analysis
- Fetch real-time:
  - videos  
  - comments  
- Perform live audience analysis  

---

## 📈 Interactive Dashboard (Streamlit)

- Dataset vs Live API toggle  
- Channel search + suggestion system  
- Filters:
  - view range  
  - category  
  - top videos  
- Visualizations:
  - sentiment distribution  
  - engagement charts  
  - performance tables  
- Risk indicator (Low / Medium / High)

---

## 🧠 Core Concept

> Many followers don’t unfollow — they simply stop engaging.

This project detects:
- passive followers  
- declining interest  
- hidden churn  

---

## 🏗️ System Pipeline

1. Data Collection (Dataset + YouTube API)  
2. Data Cleaning & Preprocessing  
3. Sentiment Analysis  
4. Engagement Analysis  
5. Quiet Quitting Detection  
6. Dashboard Visualization  

---

## 🛠️ Tech Stack

- Python  
- Pandas, NumPy  
- Streamlit (Dashboard)  
- Plotly (Visualization)  
- YouTube Data API  
- Regex & NLP Techniques  

---

## 📂 Project Structure
SMA Project/
│
├── dashboard/
│ └── app.py
│
├── src/
│ ├── clean_data.py
│ ├── sentiment_analysis.py
│ ├── engagement_analysis.py
│ ├── quiet_quitting_detector.py
│ └── youtube_api_utils.py
│
├── data/
│ ├── raw/
│ └── processed/
│
├── notebooks/
│
├── main.py
├── requirements.txt
└── README.md



---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
YOUTUBE_API_KEY=your_api_key_here
streamlit run dashboard/app.py
