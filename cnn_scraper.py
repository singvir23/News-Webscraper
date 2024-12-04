import feedparser
import requests
from bs4 import BeautifulSoup
import os

# Define a dictionary mapping categories to their respective RSS feed URLs
CATEGORY_RSS_FEEDS = {
    'world': 'http://rss.cnn.com/rss/edition_world.rss',
    'politics': 'http://rss.cnn.com/rss/edition_politics.rss',
    'science': 'http://rss.cnn.com/rss/edition_science.rss',
    'health': 'http://rss.cnn.com/rss/edition_health.rss',
    'sports': 'http://rss.cnn.com/rss/edition_sport.rss',
    'tech': 'http://rss.cnn.com/rss/edition_technology.rss'  # Assuming 'technology' is the correct RSS feed
}

def fetch_cnn_articles(rss_url):
    """Fetch articles from a given CNN RSS feed URL."""
    feed = feedparser.parse(rss_url)
    if feed.bozo:
        print(f"Failed to parse RSS feed: {rss_url}")
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
    """Extract word count, image count, image sizes, and video count from an article URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize counts
        word_count = 0
        image_count = 0
        image_sizes = []
        video_count = 0

        # Extract article content
        stories = soup.find_all('div', class_='article__content-container')
        if not stories:
            print(f"No stories found for URL: {url}")
            return word_count, image_count, image_sizes, video_count

        for story in stories:
            # Extract title
            title_tag = story.find('h2', class_='live-story-post__headline inline-placeholder')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

            # Extract text paragraphs
            text_containers = story.find_all('p', class_='paragraph inline-placeholder vossi-paragraph')
            for p in text_containers:
                text = p.get_text(separator=' ', strip=True)
                word_count += len(text.split())

            # Extract images with class 'image__dam-img'
            images_dam_img = story.find_all('img', class_='image__dam-img')

            # Extract images inside divs with class 'image_inline-small__container'
            image_small_containers = story.find_all('div', class_='image_inline-small__container')
            images_small = []
            for container in image_small_containers:
                imgs = container.find_all('img')
                images_small.extend(imgs)

            # Combine both image lists
            all_images = images_dam_img + images_small

            # To avoid counting duplicate images, we'll keep track of image sources
            seen_images = set()

            for img in all_images:
                img_src = img.get('src')
                if img_src in seen_images:
                    continue  # Skip duplicate images
                seen_images.add(img_src)

                width = img.get('width')
                height = img.get('height')

                # Exclude specific ghost images if applicable
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
                image_sizes.append(f"{width}x{height}" if width and height else "Unknown Size")

            # Extract videos
            video_containers = story.find_all('div', {'class': 'video-resource__wrapper'})
            video_count += len(video_containers)

        return word_count, image_count, image_sizes, video_count

    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return 0, 0, [], 0

def save_article_data_to_file(articles, category, filename="cnn_articles.txt"):
    """Save fetched article data to a file, avoiding duplicates."""
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

                file.write(f"Category: {category}\n")
                file.write(f"Title: {title}\n")
                file.write(f"URL: {url}\n")
                file.write(f"Date: {published_date}\n"
                           f"Word Count: {word_count} words\n"
                           f"Images: {image_count} (Sizes: {', '.join(image_sizes) if image_sizes else 'N/A'})\n"
                           f"Videos: {video_count}\n\n")
                print(f"Added article: {title} (Category: {category})")

def main():
    """Main function to fetch and save articles from all categories."""
    all_articles_fetched = False

    for category, rss_url in CATEGORY_RSS_FEEDS.items():
        print(f"Fetching articles for category: {category}")
        articles = fetch_cnn_articles(rss_url)

        if articles:
            save_article_data_to_file(articles, category, filename="cnn_articles.txt")
            all_articles_fetched = True
        else:
            print(f"No articles fetched for category: {category}")

    if all_articles_fetched:
        print("All articles have been fetched and saved.")
    else:
        print("No articles were fetched from any category.")

if __name__ == "__main__":
    main()
