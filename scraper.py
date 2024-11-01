import feedparser
import requests
from bs4 import BeautifulSoup

def fetch_fox_news_articles(rss_url):
    feed = feedparser.parse(rss_url)
    if feed.bozo:
        print("Failed to parse RSS feed.")
        return []

    articles = [
        {
            'title': entry.title,
            'url': entry.link,
            'published_date': entry.published if 'published' in entry else 'No Date Available'
        }
        for entry in feed.entries
    ]
    return articles

def get_article_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main article content section - this may require adjusting based on Fox News HTML structure
        article_section = soup.find('div', {'class': 'article-body'})  # Adjust the class name as needed

        # Extract and count words only from this section
        paragraphs = article_section.find_all('p') if article_section else []
        article_text = " ".join(p.get_text() for p in paragraphs)
        word_count = len(article_text.split())

        # Count images in the article section
        images = article_section.find_all('img') if article_section else []
        image_count = len(images)

        # Count videos in the article section
        videos = article_section.find_all('video') if article_section else []
        embeds = article_section.find_all('iframe', {'src': lambda x: 'youtube' in x or 'video' in x}) if article_section else []
        video_count = len(videos) + len(embeds)

        return word_count, image_count, video_count

    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return 0, 0, 0

def save_article_data_to_file(articles, filename="fox_news_articles.txt"):
    with open(filename, "w") as file:
        for article in articles:
            title = article['title']
            url = article['url']
            published_date = article['published_date']
            word_count, image_count, video_count = get_article_details(url)
            file.write(f"Title: {title}\nURL: {url}\nDate: {published_date}\n"
                       f"Word Count: {word_count} words\nImages: {image_count}\nVideos: {video_count}\n\n")
    print(f"Saved data for {len(articles)} articles to {filename}")

# Example usage
rss_url = "https://feeds.foxnews.com/foxnews/politics"
articles = fetch_fox_news_articles(rss_url)
save_article_data_to_file(articles)
