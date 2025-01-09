import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from urllib.parse import urljoin

def get_category_from_url(url, soup=None):
    # Extract category from URL path
    if '/world' in url:
        return 'world'
    elif '/politics' in url:
        return 'politics'
    elif '/science' in url:
        return 'science'
    elif '/health' in url:
        return 'health'
    elif '/sport' in url:
        return 'sport'
    elif '/business/tech' in url:
        return 'tech'
    elif '/tech' in url:
        return 'tech'
    return 'unknown'

def get_previously_scraped_urls(filename="cnn_articles.txt"):
    """Extract all URLs that have already been scraped from the output file"""
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
    """Update the total article count at the top of the file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'Total Articles: \d+\n\n', '', content)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total Articles: {count}\n\n{content}")
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total Articles: {count}\n\n")

def get_article_urls(url):
    """Extract article URLs from a section page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_urls = set()
        
        # Find all article containers
        containers = soup.find_all(['div', 'article'], class_=lambda x: x and ('container' in x.lower() or 'card' in x.lower()))
        
        for container in containers:
            links = container.find_all('a', href=True)
            for link in links:
                href = link['href']
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = f"https://www.cnn.com{href}"
                
                # Filter for article URLs and exclude interactive articles
                if (('/2024/' in href or '/2023/' in href) and 
                    'cnn.com' in href and 
                    '/interactive/' not in href and 
                    not href.endswith('.pdf')):
                    article_urls.add(href)
        
        return list(article_urls)
    
    except Exception as e:
        print(f"Error getting articles from {url}: {str(e)}")
        return []

def scrape_cnn_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Skip interactive articles
        if 'interactive' in soup.find_all('meta', property='og:type'):
            return None
        
        category = get_category_from_url(url)
        if category == 'unknown':
            return None
        
        result = {
            'Category': category,
            'Title': '',
            'URL': url,
            'Date': '',
            'Word Count': 0,
            'Images': []
        }
        
        # Extract title
        title = soup.find('h1')
        if title:
            result['Title'] = title.text.strip()
        
        # Extract date
        date_meta = soup.find('meta', property='article:published_time')
        if date_meta:
            date_str = date_meta.get('content')
            if date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                result['Date'] = date_obj.strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Count words in paragraphs
        paragraphs = soup.find_all(['p', 'div'], class_=lambda x: x and 'paragraph' in x.lower())
        total_words = 0
        for p in paragraphs:
            if p.text:
                words = p.text.strip().split()
                total_words += len(words)
        result['Word Count'] = f"{total_words} words"
        
        # Find images, excluding specific classes
        images = []
        all_images = soup.find_all('img', class_=lambda x: x and ('image' in x.lower() or 'photo' in x.lower()))
        for img in all_images:
            # Exclude images under byline__images, series-banner__logo-heading, and related/playlist parents
            if not img.find_parent(class_=lambda x: x and ('related' in x.lower() or 'playlist' in x.lower())) \
               and not img.find_parent(class_="byline__images") \
               and not img.find_parent(class_="series-banner__logo-heading"):
                width = img.get('width', '')
                height = img.get('height', '')
                if width and height:
                    images.append(f"{width}x{height}")
        
        result['Images'] = f"{len(images)} (Sizes: {', '.join(images)})"
        
        return result
    
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def save_article_info(info, filename="cnn_articles.txt"):
    """Save the article information to a file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"Category: {info['Category']}\n")
        f.write(f"Title: {info['Title']}\n")
        f.write(f"URL: {info['URL']}\n")
        f.write(f"Date: {info['Date']}\n")
        f.write(f"Word Count: {info['Word Count']}\n")
        f.write(f"Images: {info['Images']}\n")
        f.write("\n")

def main():
    sections = [
        "https://www.cnn.com/world",
        "https://www.cnn.com/politics",
        "https://www.cnn.com/science",
        "https://www.cnn.com/health",
        "https://www.cnn.com/sport",
        "https://www.cnn.com/business/tech"
    ]
    
    scraped_urls = get_previously_scraped_urls()
    print(f"Found {len(scraped_urls)} previously scraped articles")
    
    for section_url in sections:
        print(f"\nProcessing section: {section_url}")
        article_urls = get_article_urls(section_url)
        print(f"Found {len(article_urls)} articles in {section_url}")
        
        for url in article_urls:
            if url not in scraped_urls:
                print(f"Scraping: {url}")
                article_info = scrape_cnn_article(url)
                
                if article_info:
                    save_article_info(article_info)
                    scraped_urls.add(url)
    
    update_total_articles(len(scraped_urls))
    print("\nScraping completed. Results saved to cnn_articles.txt")

if __name__ == "__main__":
    main()
