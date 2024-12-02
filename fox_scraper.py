import feedparser
import requests
from bs4 import BeautifulSoup
import os

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

        word_count = 0
        article_content = soup.find('div', {'class': 'article-body'})
        if not article_content or not article_content.find_all('p', recursive=False):
            article_content = soup.find('div', {'class': 'paywall'})

        if article_content:
            paragraphs = article_content.find_all('p', recursive=False)
            for paragraph in paragraphs:
                word_count += len(paragraph.get_text().split())

        image_count = 0
        image_sizes = []
        video_count = 0

        if article_content:
            # Count images and gather their sizes, excluding ghost images
            images = article_content.find_all('img')
            for img in images:
                width = img.get('width')
                height = img.get('height')

                # Exclude images with width=896 and height=500
                if width and height:
                    try:
                        width_int = int(width)
                        height_int = int(height)
                        if width_int == 896 and height_int == 500:
                            continue  # Skip the ghost image
                    except ValueError:
                        # If width or height is not an integer, skip filtering
                        pass

                # If not excluded, count the image
                image_count += 1
                image_sizes.append(f"{width}x{height}")

            # Count videos
            video_containers = soup.find_all('div', {'class': 'video-container'})
            video_count = len(video_containers)

        return word_count, image_count, image_sizes, video_count

    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return 0, 0, [], 0

def save_article_data_to_file(articles, filename="fox_news_articles.txt"):
    existing_articles = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as file:
            for line in file:
                if line.startswith("URL: "):
                    url = line.split("URL: ")[1].strip()
                    existing_articles.add(url)

    with open(filename, "a", encoding='utf-8') as file:
        for article in articles:
            if article['url'] not in existing_articles:
                title = article['title']
                url = article['url']
                published_date = article['published_date']
                word_count, image_count, image_sizes, video_count = get_article_details(url)

                file.write(f"Title: {title}\nURL: {url}\nDate: {published_date}\n"
                           f"Word Count: {word_count} words\n"
                           f"Images: {image_count} (Sizes: {', '.join(image_sizes)})\n"
                           f"Videos: {video_count}\n\n")
                print(f"Added article: {title}")

# Example usage
if __name__ == "__main__":
    rss_url = "https://feeds.foxnews.com/foxnews/world"
    articles = fetch_fox_news_articles(rss_url)
    save_article_data_to_file(articles)
