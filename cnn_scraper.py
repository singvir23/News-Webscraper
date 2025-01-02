import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from urllib.parse import urljoin

def get_category_from_url(url, soup=None):
    # Extract category from span if available
    if soup:
        category_span = soup.find('span', class_='brand-logo__theme brand-logo__section-text')
        if category_span and category_span.text.strip().lower() == 'business':
            return 'tech'
        elif category_span:
            return category_span.text.strip().lower()
    
    # Fallback to URL-based category
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
    elif '/business' in url:  # Add this to catch general business URLs
        return 'tech'
    else:
        return 'unknown'

def get_previously_scraped_urls(filename="cnn_articles.txt"):
    """Extract all URLs that have already been scraped from the output file"""
    scraped_urls = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find all URLs in the file using regex
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
        
        # Remove old total if it exists
        content = re.sub(r'Total Articles: \d+\n\n', '', content)
        
        # Write new content with updated total
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total Articles: {count}\n\n{content}")
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total Articles: {count}\n\n")

def get_article_urls_from_zone(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the specified zone div
    zone_div = soup.find('div', class_='zone zone--t-light')
    article_urls = []
    
    if zone_div:
        # Find all article links within the zone
        links = zone_div.find_all('a', href=True)
        base_url = "https://www.cnn.com"
        
        for link in links:
            href = link['href']
            # Ensure we have complete URLs
            if href.startswith('/'):
                full_url = base_url + href
            else:
                full_url = href
                
            # Only include article URLs (avoid duplicates and non-article pages)
            if '/2024/' in full_url or '/2023/' in full_url:
                if full_url not in article_urls:
                    article_urls.append(full_url)
    
    return article_urls

def scrape_cnn_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            'Category': get_category_from_url(url, soup),  # Pass soup to get_category_from_url
            'Title': '',
            'URL': url,
            'Date': '',
            'Word Count': 0,
            'Images': [],
            'Videos': 0
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
        paragraphs = soup.find_all('p', class_='paragraph inline-placeholder vossi-paragraph')
        total_words = 0
        for p in paragraphs:
            if p.text:
                words = p.text.strip().split()
                total_words += len(words)
        result['Word Count'] = f"{total_words} words"
        
        # Find images excluding those in related-content and video playlist
        images = []
        all_images = soup.find_all('img', class_=lambda x: x and 'image_' in x)
        for img in all_images:
            # Check if image is in related-content or video playlist
            if (not img.find_parent('div', class_='related-content') and 
                not img.find_parent(class_=lambda x: x and 'video-playlist__items-container' in x)):
                width = img.get('width', '')
                height = img.get('height', '')
                if width and height:
                    images.append(f"{width}x{height}")
        
        result['Images'] = f"{len(images)} (Sizes: {', '.join(images)})"
        
        # Count videos with specific class and not in related-content
        videos = soup.find_all('div', {
            'data-component-name': 'video-player',
            'class': 'video-resource'
        })
        # Filter out videos in related-content
        videos = [v for v in videos if not v.find_parent('div', class_='related-content')]
        result['Videos'] = len(videos)
        
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
        f.write(f"Videos: {info['Videos']}\n")
        f.write("\n")

def main():
    # List of CNN sections to scrape
    sections = [
        "https://www.cnn.com/world",
        "https://www.cnn.com/politics",
        "https://www.cnn.com/science",
        "https://www.cnn.com/health",
        "https://www.cnn.com/sport",
        "https://www.cnn.com/business/tech"
    ]
    
    # Get already processed URLs from existing file
    scraped_urls = get_previously_scraped_urls()
    print(f"Found {len(scraped_urls)} previously scraped articles")
    
    # Process each section
    for section_url in sections:
        print(f"Processing section: {section_url}")
        article_urls = get_article_urls_from_zone(section_url)
        print(f"Found {len(article_urls)} articles in {section_url}")
        
        # Scrape each article that hasn't been processed before
        for url in article_urls:
            if url not in scraped_urls:
                print(f"Scraping: {url}")
                article_info = scrape_cnn_article(url)
                
                if article_info:
                    save_article_info(article_info)
                    scraped_urls.add(url)
    
    # Update total articles count at the top of the file
    update_total_articles(len(scraped_urls))
    print("Scraping completed. Results saved to cnn_articles.txt")

if __name__ == "__main__":
    main()