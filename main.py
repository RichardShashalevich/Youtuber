from API_KEY import API_KEY
from YouTubeAnalyzer import YouTubeAnalyzer

if __name__ == "__main__":
    QUERY    = input("Enter search query: ")
    analyzer = YouTubeAnalyzer(API_KEY, QUERY)
    analyzer.run()