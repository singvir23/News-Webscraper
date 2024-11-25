import feedparser
import requests
from bs4 import BeautifulSoup
import os

def fetch_cnn_articles(rss_url):
    """
    Fetches articles from the provided CNN RSS feed URL.

    Args:
        rss_url (str): The URL of the CNN RSS feed.

    Returns:
        list: A list of dictionaries containing article details.
    """
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
    """
    Extracts details from a CNN article page based on the provided HTML structure.

    Args:
        url (str): The URL of the CNN article.

    Returns:
        tuple: A tuple containing word count, image count, list of image sizes, video count, and PDF count.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize counts
        word_count = 0
        image_count = 0
        image_sizes = []
        video_count = 0
        pdf_count = 0

        # Extract article content
        # Each story is under a div with classes 'live-story-post liveStoryPost'
        stories = soup.find_all('div', class_='live-story-post liveStoryPost')
        if not stories:
            print(f"No stories found for URL: {url}")
            return word_count, image_count, image_sizes, video_count, pdf_count

        for story in stories:
            # Extract title
            title_tag = story.find('h2', class_='live-story-post__headline inline-placeholder')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

            # Extract text paragraphs
            text_containers = story.find_all('p', class_='inline-placeholder vossi-paragraph')
            for p in text_containers:
                text = p.get_text(separator=' ', strip=True)
                word_count += len(text.split())

            # Extract images
            images = story.find_all('img', class_='image__picture')
            for img in images:
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
            video_containers = story.find_all('div', class_='Flex-sc-1sqrs56-0 pui_unplayed-slate player-user-interfacestyles__UnplayedSlateContainer-sc-18ilyu6-3 iYfaHb')
            video_count += len(video_containers)

            # Extract PDFs
            pdf_links = story.find_all('a', href=True)
            for link in pdf_links:
                if link['href'].lower().endswith('.pdf'):
                    pdf_count += 1

        return word_count, image_count, image_sizes, video_count, pdf_count

    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return 0, 0, [], 0, 0

def save_article_data_to_file(articles, filename="cnn_articles.txt"):
    """
    Saves article data to a text file, avoiding duplicates.

    Args:
        articles (list): A list of dictionaries containing article details.
        filename (str, optional): The name of the file to save data. Defaults to "cnn_articles.txt".
    """
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
                word_count, image_count, image_sizes, video_count, pdf_count = get_article_details(url)

                file.write(f"Title: {title}\nURL: {url}\nDate: {published_date}\n"
                           f"Word Count: {word_count} words\n"
                           f"Images: {image_count} (Sizes: {', '.join(image_sizes) if image_sizes else 'N/A'})\n"
                           f"Videos: {video_count}\nPDFs: {pdf_count}\n\n")
                print(f"Added article: {title}")

# Example usage
if __name__ == "__main__":
    # CNN RSS feed URL for World News
    rss_url = "http://rss.cnn.com/rss/edition_world.rss"
    
    # Fetch articles from CNN RSS feed
    articles = fetch_cnn_articles(rss_url)
    
    if articles:
        # Save fetched article data to file
        save_article_data_to_file(articles, filename="cnn_articles.txt")
    else:
        print("No articles fetched.")
