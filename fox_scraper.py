import feedparser
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime, timezone
import email.utils

CUSTOM_RSS_LINKS = {
    "politics": "https://moxie.foxnews.com/google-publisher/politics.xml",
    "science": "https://moxie.foxnews.com/google-publisher/science.xml",
    "health": "https://moxie.foxnews.com/google-publisher/health.xml",
    "sports": "https://moxie.foxnews.com/google-publisher/sports.xml",
}

DEFAULT_BASE_URL = "https://feeds.foxnews.com/foxnews/"
CATEGORIES = ["politics", "science", "health", "sports"]

# Constants for filtering
MAX_WORD_COUNT = 3000
MAX_IMAGE_COUNT = 10

def parse_date(date_str):
    """Parse date string to datetime object."""
    try:
        # Parse RFC 2822 date format
        return datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date_str)), timezone.utc)
    except:
        try:
            # Try parsing other common date formats
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
        except:
            return None

def is_within_date_range(date_str):
    """Check if the article date is within the specified range."""
    date = parse_date(date_str)
    if not date:
        return False
    
    start_date = datetime(2024, 12, 15, tzinfo=timezone.utc)
    end_date = datetime(2025, 2, 17, tzinfo=timezone.utc)
    
    return start_date <= date <= end_date

def is_valid_article(word_count, image_count):
    """Check if article meets the filtering criteria."""
    return word_count <= MAX_WORD_COUNT and image_count <= MAX_IMAGE_COUNT

def fetch_fox_news_articles(rss_url):
    feed = feedparser.parse(rss_url)
    if feed.bozo:
        print(f"Failed to parse RSS feed for {rss_url}.")
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
        response = requests.get(url, timeout=10)
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

        if article_content:
            images = article_content.find_all('img')
            for img in images:
                width = img.get('width')
                height = img.get('height')

                if width and height:
                    try:
                        width_int = int(width)
                        height_int = int(height)
                        if width_int == 896 and height_int == 500:
                            continue
                    except ValueError:
                        pass

                image_count += 1
                image_sizes.append(f"{width}x{height}" if width and height else "Unknown Size")

        return word_count, image_count, image_sizes

    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return 0, 0, []
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        return 0, 0, []

def update_total_articles_count(filename):
    if not os.path.exists(filename):
        return

    with open(filename, "r", encoding='utf-8') as file:
        lines = file.readlines()

    article_count = sum(1 for line in lines if line.startswith("Category:"))

    if lines and lines[0].startswith("Total Articles:"):
        lines[0] = f"Total Articles: {article_count}\n"
    else:
        lines.insert(0, f"Total Articles: {article_count}\n")

    with open(filename, "w", encoding='utf-8') as file:
        file.writelines(lines)

def save_article_data_to_file(articles, category, filename="./article-visualization/public/data/fox_news_articles.txt"):
    existing_articles = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as file:
            for line in file:
                if line.startswith("URL: "):
                    url = line.split("URL: ")[1].strip()
                    existing_articles.add(url)

    new_articles_added = 0
    with open(filename, "a", encoding='utf-8') as file:
        for article in articles:
            if article['url'] not in existing_articles:
                title = article['title']
                url = article['url']
                published_date = article['published_date']
                
                # Check if article is within date range before processing further
                if not is_within_date_range(published_date):
                    print(f"Skipping article outside date range: {title}")
                    continue
                
                word_count, image_count, image_sizes = get_article_details(url)

                # Check if article meets criteria before saving
                if not is_valid_article(word_count, image_count):
                    print(f"Skipping article due to filtering criteria: {title}")
                    continue

                image_sizes_str = ", ".join(image_sizes) if image_sizes else "No Images"

                file.write(
                    f"Category: {category}\n"
                    f"Title: {title}\n"
                    f"URL: {url}\n"
                    f"Date: {published_date}\n"
                    f"Word Count: {word_count} words\n"
                    f"Images: {image_count} (Sizes: {image_sizes_str})\n\n"
                )
                print(f"Added article from {category}: {title}")
                new_articles_added += 1

    if new_articles_added > 0:
        update_total_articles_count(filename)

def clean_existing_file(filename="./article-visualization/public/data/fox_news_articles.txt"):
    """Clean existing file by removing articles that don't meet the criteria."""
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return

    print("Cleaning existing file...")
    
    with open(filename, "r", encoding='utf-8') as file:
        content = file.read()

    # Split content into article blocks
    articles = content.split("\n\n")
    
    # First block might be the total count, preserve it if it exists
    header = articles[0] if articles[0].startswith("Total Articles:") else None
    if header:
        articles = articles[1:]

    cleaned_articles = []
    for article in articles:
        if not article.strip():
            continue
            
        # Parse word count and image count
        word_count_match = re.search(r"Word Count: (\d+)", article)
        image_count_match = re.search(r"Images: (\d+)", article)
        date_match = re.search(r"Date: (.+)", article)
        
        if word_count_match and image_count_match and date_match:
            word_count = int(word_count_match.group(1))
            image_count = int(image_count_match.group(1))
            date_str = date_match.group(1).strip()
            
            # Check both content criteria and date range
            if is_valid_article(word_count, image_count) and is_within_date_range(date_str):
                cleaned_articles.append(article)
            else:
                print(f"Removing article with {word_count} words, {image_count} images, date: {date_str}")

    # Write cleaned content back to file
    with open(filename, "w", encoding='utf-8') as file:
        if header:
            file.write(header + "\n\n")
        file.write("\n\n".join(cleaned_articles))
        if cleaned_articles:
            file.write("\n\n")  # Add final newlines

    update_total_articles_count(filename)
    print("File cleaning completed.")

def scrape_all_categories():
    for category in CATEGORIES:
        rss_url = CUSTOM_RSS_LINKS.get(category, f"{DEFAULT_BASE_URL}{category}")
        print(f"Scraping category: {category}")
        articles = fetch_fox_news_articles(rss_url)
        if articles:
            save_article_data_to_file(articles, category)
        else:
            print(f"No articles found for category: {category}")

if __name__ == "__main__":
    scrape_all_categories()
    clean_existing_file()  # Clean the file after scraping to ensure all articles meet criteria