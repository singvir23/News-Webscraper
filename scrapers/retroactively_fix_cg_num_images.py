import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import time
from sqlalchemy import text
def count_images_and_svgs(html):
    soup = BeautifulSoup(html, 'html.parser')
    img_count = len(soup.find_all('img'))
    svg_count = len(soup.find_all('svg'))
    return img_count + svg_count

def main():
    # Connect to the database
    engine = create_engine(
        "postgresql+psycopg2://scraperdb_owner:npg_mbyWDf3q5rFp@ep-still-snowflake-a4l5opga-pooler.us-east-1.aws.neon.tech/scraperdb?sslmode=require"
    )
    # Load Capitol Gazette articles
    df = pd.read_sql_query("SELECT id, url, num_images FROM capitol_gazette;", engine)
    print(f"Loaded {len(df)} Capitol Gazette articles.")
    
    updated = 0
    for idx, row in df.iterrows():
        url = row['url']
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                n_images = count_images_and_svgs(resp.text)
                # Only update if the count is different
                if n_images != row['num_images']:
                    with engine.begin() as conn:

                        conn.execute(
                            text("""
                                UPDATE capitol_gazette
                                SET num_images = :n_images
                                WHERE id = :id
                            """),
                            {"n_images": n_images, "id": row['id']}
                        )

                    print(f"Updated article {row['id']} ({url}): num_images = {n_images}")
                    updated += 1
            else:
                print(f"Failed to fetch {url} (status {resp.status_code})")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        print(f"Progress: {idx + 1}/{len(df)} ({(idx + 1) / len(df) * 100:.1f}%)")
        time.sleep(0.5)  
    print(f"Done. Updated {updated} articles.")

if __name__ == "__main__":
    main()
