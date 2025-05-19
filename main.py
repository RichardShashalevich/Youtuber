import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import pandas as pd
from API_KEY import API_KEY
# --- Settings ---

# QUERY = "scary stories -prank -comedy"
QUERY = input("Enter search query: ")
MAX_RESULTS = 200
MIN_SUBSCRIBERS = 1000
MAX_SUBSCRIBERS = 100000
OUTPUT_FILE = "youtube_analysis.csv"

# --- Flexible time settings ---
TIME_FILTER = {
    'year': 2024,         # Example: 2023
    'month': None,        # Example: 5 (May)
    'season': None,       # 'winter','spring','summer','autumn'
    'last_days': None,    # Example: 7 (week)
    'custom_range': None  # Example: {'start':'2024-01-01', 'end':'2024-03-31'}
}

# --- Initialize API ---
youtube = build("youtube", "v3", developerKey=API_KEY)
channel_cache = {}

def get_date_range():
    """Flexible date range calculation"""
    now = datetime.now()
    
    if TIME_FILTER.get('custom_range'):
        start = datetime.strptime(TIME_FILTER['custom_range']['start'], '%Y-%m-%d')
        end = datetime.strptime(TIME_FILTER['custom_range']['end'], '%Y-%m-%d')
        return start, end
    
    if TIME_FILTER.get('last_days'):
        start = now - timedelta(days=TIME_FILTER['last_days'])
        return start, now
    
    if TIME_FILTER.get('year'):
        year = TIME_FILTER['year']
    else:
        year = now.year

    if TIME_FILTER.get('season'):
        seasons = {
            'winter': (12, 1, 2),
            'spring': (3, 4, 5),
            'summer': (6, 7, 8),
            'autumn': (9, 10, 11)
        }
        months = seasons[TIME_FILTER['season']]
        start = datetime(year, months[0], 1)
        end = datetime(year if months[0] != 12 else year + 1, months[-1], 28) + timedelta(days=4)
        return start, end
    
    if TIME_FILTER.get('month'):
        start = datetime(year, TIME_FILTER['month'], 1)
        end = datetime(year, TIME_FILTER['month'], 28) + timedelta(days=4)
        return start, end
    
    return datetime(year, 1, 1), datetime(year, 12, 31)

def get_channel_subscribers(channel_id):
    """Caching subscriber count request"""
    if channel_id not in channel_cache:
        try:
            response = youtube.channels().list(
                part="statistics",
                id=channel_id
            ).execute()
            channel_cache[channel_id] = int(response["items"][0]["statistics"]["subscriberCount"])
        except:
            return None
    return channel_cache[channel_id]

def get_videos():
    """Main data collection"""
    try:
        start_date, end_date = get_date_range()
        print(f"Analyzing videos for the period: {start_date.date()} — {end_date.date()}")
        
        search_response = youtube.search().list(
            q=QUERY,
            part="id,snippet",
            type="video",
            order="relevance",
            maxResults=MAX_RESULTS,
            publishedAfter=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            publishedBefore=end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            relevanceLanguage="en"
        ).execute()

        videos = []
        for item in search_response.get("items", []):
            try:
                video_id = item["id"]["videoId"]
                stats = youtube.videos().list(
                    part="statistics,contentDetails",
                    id=video_id
                ).execute()["items"][0]
                
                subs = get_channel_subscribers(item["snippet"]["channelId"])
                if not subs or not MIN_SUBSCRIBERS <= subs <= MAX_SUBSCRIBERS:
                    continue
                
                videos.append({
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "views": int(stats["statistics"].get("viewCount", 0)),
                    "likes": int(stats["statistics"].get("likeCount", 0)),
                    "comments": int(stats["statistics"].get("commentCount", 0)),
                    "subscribers": subs,
                    "published_at": item["snippet"]["publishedAt"],
                    "url": f"https://youtu.be/{video_id}"
                    })
                
            except Exception as e:
                print(f"Error processing video: {str(e)}")
            
            time.sleep(0.5)
        
        return videos
    
    except Exception as e:
        print(f"Request error: {str(e)}")
        return []

def analyze_and_save(videos):
    """Analysis and saving with different sorting criteria"""
    if not videos:
        print("No videos match the criteria.")
        return
    
    df = pd.DataFrame(videos)
    df["published_at"] = pd.to_datetime(df["published_at"])    
    # Calculate metrics
    df["views_per_sub"] = df["views"] / df["subscribers"].replace(0, 1)
    df["like_ratio"] = df["likes"] / df["views"].replace(0, 1)

    df_views = df.sort_values("views", ascending=False)
    df_virality = df.sort_values("views_per_sub", ascending=False)
    df_engagement = df.sort_values("like_ratio", ascending=False)
    
    # Save to separate files
    df_views.to_csv("top_views.csv", index=False)
    df_virality.to_csv("top_virality.csv", index=False)
    df_engagement.to_csv("top_engagement.csv", index=False)
    
    print(f"\nVideos found: {len(df)}")
    # print("\nTop by relevance:")
    # print(df[["title", "channel", "views", "like_ratio"]].head(10).to_string(index=False))
    
    # Top-5 by different criteria
    print("\nTop-5 by views:")
    print(df_views[["title", "channel", "subscribers", "views", "published_at"]].head(5).to_string(index=False))
    
    print("\nTop-5 by virality (views/subscriber):")
    print(df_virality[["title", "channel", "subscribers", "views_per_sub", "published_at"]].head(10).to_string(index=False))
    
    print("\nTop-5 by engagement (like_ratio):")
    print(df_engagement[["title", "channel", "subscribers", "like_ratio", "published_at"]].head(5).to_string(index=False))
    
    # Save all data
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nAll results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    print(f"Analysis for query: '{QUERY}'")
    videos = get_videos()
    analyze_and_save(videos)