import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urljoin

def get_category_from_url(url):
    """Determine category from the URL path."""
    if '/politics' in url:
        return 'politics'
    elif '/science' in url:
        return 'science'
    elif '/health' in url:
        return 'health'
    elif '/sport' in url:
        return 'sports'
    return 'unknown'

def get_previously_scraped_urls(filename="cnn_articles.txt"):
    """Extract all URLs that have already been scraped from the output file."""
    scraped_urls = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            urls = re.findall(r'URL: (.*?)\n', content)
            scraped_urls.update(urls)
    except FileNotFoundError:
        pass
    return scraped_urls

def update_total_articles(count, filename="cnn_articles.txt"):
    """Update the total article count at the top of the file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.readlines()

        if content and content[0].startswith("Total Articles:"):
            content.pop(0)

        content.insert(0, f"Total Articles: {count}\n\n")

        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(content)

    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total Articles: {count}\n\n")

def get_article_urls_from_containers(url, containers):
    """Extract article URLs from the specified containers on the page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_urls = set()

        for container_class in containers:
            container = soup.find('div', class_=container_class)
            if container:
                links = container.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.startswith('/'):
                        href = urljoin(url, href)
                    if ('cnn.com' in href and '/interactive/' not in href and not href.endswith('.pdf')):
                        article_urls.add(href)
        return list(article_urls)
    except Exception:
        return []

def scrape_cnn_article(url, override_category=None):
    """Scrape an individual CNN article for information."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        category = override_category if override_category else get_category_from_url(url)
        if category == 'unknown':
            print(f"Skipping article with unknown category: {url}")
            return None

        result = {
            'Category': category,
            'Title': '',
            'URL': url,
            'Date': '',
            'Word Count': 0,
            'Images': []
        }

        title = soup.find('h1')
        if title:
            result['Title'] = title.text.strip()

        date_meta = soup.find('meta', property='article:published_time')
        if date_meta:
            date_str = date_meta.get('content')
            if date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                result['Date'] = date_obj.strftime('%a, %d %b %Y %H:%M:%S %z')

        paragraphs = soup.find_all(['p', 'div'], class_=lambda x: x and 'paragraph' in x.lower())
        total_words = sum(len(p.text.split()) for p in paragraphs if p.text)
        result['Word Count'] = f"{total_words} words"

        images = []
        all_images = soup.find_all('img', class_=lambda x: x and ('image' in x.lower() or 'photo' in x.lower()))
        for img in all_images:
            if not img.find_parent(class_=lambda x: x and ('related' in x.lower() or 'playlist' in x.lower())) \
               and not img.find_parent(class_="byline__images") \
               and not img.find_parent(class_="series-banner__logo-heading") \
               and not img.find_parent(class_="container_list-headlines-with-images__cards-wrapper") \
               and not img.find_parent(class_="container__item-media  container_list-headlines-with-images__item-media"):
                width = img.get('width', '')
                height = img.get('height', '')
                if width and height:
                    images.append(f"{width}x{height}")
        result['Images'] = f"{len(images)} (Sizes: {', '.join(images)})"

        if not result['Title'] or not result['Date'] or total_words == 0:
            print(f"Skipping incomplete article: {url}")
            return None

        return result

    except Exception:
        print(f"Error scraping article: {url}")
        return None

def save_article_info(info, filename="cnn_articles.txt"):
    """Save the article information to a file."""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"Category: {info['Category']}\n")
        f.write(f"Title: {info['Title']}\n")
        f.write(f"URL: {info['URL']}\n")
        f.write(f"Date: {info['Date']}\n")
        f.write(f"Word Count: {info['Word Count']}\n")
        f.write(f"Images: {info['Images']}\n")
        f.write("\n")

def main():
    sections = {
        "https://www.cnn.com/world": [
            'container__field-links container_lead-plus-headlines-with-images__field-links',
            'container__field-links container_lead-plus-headlines__field-links',
            'container__field-links container_vertical-strip__field-links'
        ],
        "https://www.cnn.com/politics": [
            'container__field-links container_lead-plus-headlines__field-links',
            'container__field-links container_vertical-strip__field-links'
        ],
        "https://www.cnn.com/science": [
            'container__field-links container_lead-plus-headlines-with-images__field-links'
        ],
        "https://www.cnn.com/health": [
            'container__field-links container_lead-plus-headlines__field-links'
        ],
        "https://www.cnn.com/sport": [
            'container__field-links container_lead-plus-headlines__field-links'
        ]
    }

    scraped_urls = get_previously_scraped_urls()
    print(f"Found {len(scraped_urls)} previously scraped articles")

    for section_url, containers in sections.items():
        print(f"\nProcessing section: {section_url}")
        article_urls = get_article_urls_from_containers(section_url, containers)
        print(f"Found {len(article_urls)} articles in {section_url}")

        for url in article_urls:
            if url not in scraped_urls:
                print(f"Scraping: {url}")
                override_category = 'world' if 'world' in section_url else None
                article_info = scrape_cnn_article(url, override_category)
                if article_info:
                    save_article_info(article_info)
                    scraped_urls.add(url)

    update_total_articles(len(scraped_urls))
    print("\nScraping completed. Results saved to cnn_articles.txt")

if __name__ == "__main__":
    main()