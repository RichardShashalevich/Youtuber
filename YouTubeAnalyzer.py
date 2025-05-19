import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import pandas as pd
from API_KEY import API_KEY
from word_analyser import count_words

MAX_RESULTS = 50
LANGUAGE = "en"
MIN_SUBSCRIBERS = 1000
MAX_SUBSCRIBERS = 1000000
OUTPUT_FILE = "youtube_analysis.csv"
TIME_FILTER = {
    'year': 2024,
    'month': None,
    'season': None,
    'last_days': None,
    'custom_range': None
}

class YouTubeAnalyzer:
    def __init__(self, api_key, query):
        self.youtube = build("youtube", "v3", developerKey=api_key)
        self.channel_cache = {}
        self.query = query

    def get_date_range(self):
        now = datetime.now()
        if TIME_FILTER.get('custom_range'):
            start = datetime.strptime(TIME_FILTER['custom_range']['start'], '%Y-%m-%d')
            end = datetime.strptime(TIME_FILTER['custom_range']['end'], '%Y-%m-%d')
            return start, end
        if TIME_FILTER.get('last_days'):
            return now - timedelta(days=TIME_FILTER['last_days']), now
        year = TIME_FILTER.get('year') or now.year
        if TIME_FILTER.get('season'):
            seasons = {
                'winter': (12, 1, 2),
                'spring': (3, 4, 5),
                'summer': (6, 7, 8),
                'autumn': (9, 10, 11)
            }
            months = seasons[TIME_FILTER['season']]
            start = datetime(year, months[0], 1)
            end = datetime(year if months[0] != 12 else year + 1,
                           months[-1], 28) + timedelta(days=4)
            return start, end
        if TIME_FILTER.get('month'):
            start = datetime(year, TIME_FILTER['month'], 1)
            end = datetime(year, TIME_FILTER['month'], 28) + timedelta(days=4)
            return start, end
        return datetime(year, 1, 1), datetime(year, 12, 31)

    def get_channel_subscribers(self, channel_id):
        return (self.channel_cache.get(channel_id) or
                self.calculate_channel_subscribers(channel_id))

    def calculate_channel_subscribers(self, channel_id):
        try:
            resp = self.youtube.channels().list(
                part="statistics", id=channel_id
            ).execute()
            self.channel_cache[channel_id] = int(
                resp["items"][0]["statistics"]["subscriberCount"]
            )
        except:
            return None
        return self.channel_cache[channel_id]

    def search_request(self, start_date, end_date, page_token=None):
        per_page = 50
        return self.youtube.search().list(
            q=self.query,
            part="id,snippet",
            type="video",
            order="relevance",
            maxResults=per_page,
            publishedAfter=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            publishedBefore=end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            relevanceLanguage=LANGUAGE,
            pageToken=page_token
        ).execute()

    def get_video_stats(self, video_id):
        return self.youtube.videos().list(
            part="statistics,contentDetails", id=video_id
        ).execute()["items"][0]

    def process_video_item(self, item):
        video_id = item["id"]["videoId"]
        try:
            stats = self.get_video_stats(video_id)
        except Exception as e:
            print(f"Error processing video: {e}")
            return None
        subs = self.get_channel_subscribers(item["snippet"]["channelId"])
        if not subs or not MIN_SUBSCRIBERS <= subs <= MAX_SUBSCRIBERS:
            return None
        return {
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "views": int(stats["statistics"].get("viewCount", 0)),
            "likes": int(stats["statistics"].get("likeCount", 0)),
            "comments": int(stats["statistics"].get("commentCount", 0)),
            "subscribers": subs,
            "published_at": item["snippet"]["publishedAt"],
            "description": item["snippet"].get("description", ""),
            "url": f"https://youtu.be/{video_id}"
        }

    def get_videos(self):
        start_date, end_date = self.get_date_range()
        print(f"Analyzing videos for: {start_date.date()} — {end_date.date()}")
        videos, processed, page_token = [], 0, None
        while True:
            try:
                resp = self.search_request(start_date, end_date, page_token)
            except Exception as e:
                print(f"Request error: {e}")
                return []
            for item in resp.get("items", []):
                data = self.process_video_item(item)
                if data:
                    videos.append(data)
                processed += 1
                if processed >= MAX_RESULTS:
                    break
            if processed >= MAX_RESULTS or not resp.get("nextPageToken"):
                break
            page_token = resp["nextPageToken"]
        return videos

    def analyze_and_save(self, videos):
        if not videos:
            print("No matching videos.")
            return
        df = pd.DataFrame(videos)
        df["published_at"] = pd.to_datetime(df["published_at"])
        df["views_per_sub"]   = df["views"]   / df["subscribers"].replace(0,1)
        df["like_ratio"]      = df["likes"]   / df["views"].replace(0,1)
        df.sort_values("views",ascending=False).to_csv("top_views.csv",      index=False)
        df.sort_values("views_per_sub",ascending=False).to_csv("top_virality.csv", index=False)
        df.sort_values("like_ratio",ascending=False).to_csv("top_engagement.csv",index=False)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nAll results saved to {OUTPUT_FILE}")

        # --- count words in titles & descriptions separately ---
        all_titles      = " ".join(v["title"]      for v in videos)
        all_descriptions= " ".join(v["description"]for v in videos)
        title_map = count_words(all_titles)
        desc_map  = count_words(all_descriptions)

        print("\nTop-10 words in titles:")
        for w, c in title_map.most_common(10):
            print(f"{w}: {c}")

        print("\nTop-10 words in descriptions:")
        for w, c in desc_map.most_common(10):
            print(f"{w}: {c}")

        title_items = title_map.most_common()
        pd.DataFrame(title_items, columns=["word", "count"]) \
            .to_csv("title_word_counts.csv", index=False)
        desc_items  = desc_map.most_common()
        pd.DataFrame(desc_items, columns=["word", "count"]) \
            .to_csv("description_word_counts.csv", index=False)

    def run(self):
        videos = self.get_videos()
        self.analyze_and_save(videos)
