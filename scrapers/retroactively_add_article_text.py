import psycopg2
import json
from bs4 import BeautifulSoup
import requests
import time

DB_URL = "postgresql://scraperdb_owner:npg_mbyWDf3q5rFp@ep-still-snowflake-a4l5opga-pooler.us-east-1.aws.neon.tech/scraperdb?sslmode=require"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def get_soup(url: str) -> BeautifulSoup:
    resp = SESSION.get(url, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def extract_article_text(url: str) -> str:
    soup = get_soup(url)
    paragraphs = soup.select("div.body-copy p")
    text = " ".join(p.get_text(strip=True) for p in paragraphs)
    return text

def main():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()

    # Find articles missing article_text or where it's null/empty
    cur.execute("SELECT url FROM capitol_gazette WHERE article_text IS NULL OR article_text = '';")
    rows = cur.fetchall()
    print(f"Found {len(rows)} articles missing text.")
    updated = 0
    for (url,) in rows:
        try:
            text = extract_article_text(url)
            cur.execute(
                "UPDATE capitol_gazette SET article_text = %s WHERE url = %s;",
                (text, url)
            )
            updated += 1
            print(f"Updated: {url}")
        except Exception as exc:
            print(f"Failed {url}: {exc}")
        time.sleep(0.6)
    cur.close()
    conn.close()
    print(f"Done. Updated {updated} articles.")

if __name__ == "__main__":
    main()
