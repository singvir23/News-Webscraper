import pandas as pd
from sqlalchemy import create_engine, text
from geopy.geocoders import Nominatim
import spacy
import time
from tqdm import tqdm

# Connect to PostgreSQL
engine = create_engine(
    "postgresql+psycopg2://scraperdb_owner:npg_mbyWDf3q5rFp@ep-still-snowflake-a4l5opga-pooler.us-east-1.aws.neon.tech/scraperdb?sslmode=require"
)

# Load spaCy and geolocator
nlp = spacy.load("en_core_web_sm")
geolocator = Nominatim(user_agent="place_mapper", timeout=10)

# Create article_place_mentions table if it doesn't exist
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS article_place_mentions (
            id SERIAL PRIMARY KEY,
            headline TEXT,
            place TEXT,
            source TEXT,
            url TEXT,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION
        );
    """))

# Load article data
query = """
SELECT headline, article_text, url, headline_len, 'Capitol Gazette' AS source FROM capitol_gazette
WHERE headline IS NOT NULL AND headline_len > 0
UNION ALL
SELECT headline, article_text, url, headline_len, 'Baltimore Banner' AS source FROM baltimore_banner
WHERE headline IS NOT NULL AND headline_len > 0;
"""
df = pd.read_sql(query, engine)

# Extract GPEs from headline + article text
def extract_places(text):
    doc = nlp(str(text))
    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]

df["places"] = (df["headline"].fillna("") + " " + df["article_text"].fillna("")).apply(extract_places)
mentions = df.explode("places").dropna(subset=["places"])[["headline", "places", "source", "url"]].drop_duplicates()

# Load cached locations
existing = pd.read_sql("SELECT * FROM location_cache", engine)
existing_dict = dict(zip(existing["place"], zip(existing["latitude"], existing["longitude"])))

# Geocode new places
new_places = set(mentions["places"]) - set(existing_dict)
new_rows = []

print(f"🧭 Geocoding {len(new_places)} new places...")

for place in tqdm(new_places, desc="🌍 Geocoding"):
    #time.sleep(0.5)
    try:
        location = geolocator.geocode(place)
        if location:
            lat, lon = location.latitude, location.longitude
            new_rows.append((place, lat, lon))
            existing_dict[place] = (lat, lon)
        else:
            existing_dict[place] = (None, None)
            print(f"❌ Geocode not found for {place}")
    except Exception as e:
        print(f"❌ Error geocoding {place}: {e}")
        existing_dict[place] = (None, None)


# Save before DB insert (backup in case of failure)
mentions.to_csv("article_place_mentions_backup.csv", index=False)
print("📁 Backup saved to 'article_place_mentions_backup.csv'")

# Insert new geocodes into location_cache
with engine.begin() as conn:
    if new_rows:
        conn.execute(
            text("""
                INSERT INTO location_cache (place, latitude, longitude)
                VALUES (:p, :lat, :lon)
                ON CONFLICT (place) DO NOTHING
            """),
            [{"p": place, "lat": lat, "lon": lon} for place, lat, lon in new_rows]
        )


# Add lat/lon to mentions
mentions["latitude"] = mentions["places"].map(lambda p: existing_dict.get(p, (None, None))[0])
mentions["longitude"] = mentions["places"].map(lambda p: existing_dict.get(p, (None, None))[1])

def clean_place(p):
    return p if len(p) > 2 and p.isalpha() else None

mentions["places"] = mentions["places"].map(clean_place)
mentions = mentions.dropna(subset=["places"])

# Insert article-place-location links
with engine.begin() as conn:
    for _, row in mentions.iterrows():
        conn.execute(
            text("""
                INSERT INTO article_place_mentions (headline, place, source, url, latitude, longitude)
                VALUES (:headline, :place, :source, :url, :lat, :lon)
                ON CONFLICT DO NOTHING
            """),
            {
                "headline": row["headline"],
                "place": row["places"],
                "source": row["source"],
                "url": row["url"],
                "lat": row["latitude"],
                "lon": row["longitude"]
            }
        )

print("✅ All geocoded article-place entries saved to 'article_place_mentions' table.")
