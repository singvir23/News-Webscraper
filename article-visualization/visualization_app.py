import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import pydeck as pdk
import datetime


# Streamlit config
st.set_page_config(page_title="News Visualizer", layout="wide")
st.title("📰 Combined News Articles Visualization Dashboard")

# Load data from PostgreSQL
@st.cache_data(ttl=600)
def load_data():
    engine = create_engine(
        "postgresql+psycopg2://scraperdb_owner:npg_mbyWDf3q5rFp@ep-still-snowflake-a4l5opga-pooler.us-east-1.aws.neon.tech/scraperdb?sslmode=require"
    )
    bb = pd.read_sql_query("SELECT * FROM baltimore_banner;", engine)
    cg = pd.read_sql_query("SELECT * FROM capitol_gazette;", engine)

    bb["source"] = "Baltimore Banner"
    cg["source"] = "Capitol Gazette"

    df = pd.concat([bb, cg], ignore_index=True)

    df = df.dropna(subset=["headline", "pub_date"])
    df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")
    df = df.dropna(subset=["pub_date"])

    # Filter out invalid entries
    df = df[(df["headline_len"] > 0) & (df["word_count"] > 0)]

    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

sources = st.sidebar.multiselect(
    "Select News Sources",
    options=df["source"].unique(),
    default=df["source"].unique()
)

sections = st.sidebar.multiselect(
    "Select Sections",
    options=sorted(df["section"].dropna().unique()),
    default=sorted(df["section"].dropna().unique())
)

# Set default dates in the sidebar
default_start_date = datetime.date(2025, 4, 20)
default_end_date = df["pub_date"].max()


date_min, date_max = df["pub_date"].min(), df["pub_date"].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[default_start_date, default_end_date],
    min_value=date_min,
    max_value=date_max
)

# Filtered data
filtered = df[
    (df["source"].isin(sources)) &
    (df["section"].isin(sections)) &
    (df["pub_date"] >= pd.to_datetime(date_range[0])) &
    (df["pub_date"] <= pd.to_datetime(date_range[1]))
]

#---------------MAP Section--------------------
import pydeck as pdk

# Load geocoded place mentions from the DB
@st.cache_data(ttl=600)
def load_place_mentions():
    engine = create_engine(
        "postgresql+psycopg2://scraperdb_owner:npg_mbyWDf3q5rFp@ep-still-snowflake-a4l5opga-pooler.us-east-1.aws.neon.tech/scraperdb?sslmode=require"
    )
    return pd.read_sql("SELECT * FROM article_place_mentions", engine)

# Load and filter by sidebar-selected articles
all_place_mentions = load_place_mentions()
place_df = all_place_mentions.merge(
    filtered[["headline"]], on="headline", how="inner"
)

# Create clickable link for each headline
place_df["headline_link"] = place_df.apply(
    lambda row: f"<a href='{row.url}' target='_blank'>{row.headline}</a>", axis=1
)

# Group and join headlines into one per place
headline_links = (
    place_df.groupby(["place", "latitude", "longitude"])["headline_link"]
    .apply(lambda links: "<br>".join(links))
    .reset_index()
)

# Count mentions per source
source_counts = (
    place_df.groupby(["place", "latitude", "longitude", "source"])
    .size()
    .reset_index(name="source_count")
)

# Pivot source counts into columns
source_pivot = source_counts.pivot_table(
    index=["place", "latitude", "longitude"],
    columns="source",
    values="source_count",
    fill_value=0
).reset_index()

# Ensure expected columns exist even if one source is missing
for col in ["Baltimore Banner", "Capitol Gazette"]:
    if col not in source_pivot.columns:
        source_pivot[col] = 0

# Rename for consistency
source_pivot.columns.name = None
source_pivot = source_pivot.rename(columns={
    "Baltimore Banner": "banner_count",
    "Capitol Gazette": "gazette_count"
})

# Total mentions and scaled radius
source_pivot["total_mentions"] = source_pivot["banner_count"] + source_pivot["gazette_count"]
source_pivot["scaled_radius"] = (source_pivot["total_mentions"] + 20) * 2000

# Assign color based on source mix
def get_color(row):
    if row["banner_count"] > 0 and row["gazette_count"] > 0:
        return [160, 32, 240, 200]  # purple
    elif row["banner_count"] > 0:
        return [255, 0, 0, 200]      # red
    else:
        return [0, 100, 255, 200]    # blue

source_pivot["dot_color"] = source_pivot.apply(get_color, axis=1)

# Merge everything
map_data = source_pivot.merge(headline_links, on=["place", "latitude", "longitude"], how="left")

# Build map
st.subheader("🗺️ Map of Places Mentioned in Articles")
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=map_data["latitude"].mean(),
        longitude=map_data["longitude"].mean(),
        zoom=3,
        pitch=0
    ),
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position='[longitude, latitude]',
            get_radius="scaled_radius",
            get_fill_color="dot_color",
            pickable=True,
            radius_scale=1,            # Base radius scaling factor
            radius_min_pixels=2,       # Min size regardless of zoom
            radius_max_pixels=40,      # Max size regardless of zoom
            auto_highlight=True
        ),  
    ],
    tooltip={
        "html": """
            <b>{place}</b><br>
            Baltimore Banner Mentions: {banner_count}<br>
            Capitol Gazette Mentions: {gazette_count}<br>
        """,
        "style": {"color": "white", "maxWidth": "400px"}
    }
), height=700)




# Charts
st.subheader("📅 Articles Over Time")
fig_time = px.histogram(filtered, x="pub_date", color="source", nbins=40, title="Publication Timeline by Source")
st.plotly_chart(fig_time, use_container_width=True)

st.subheader("✍️ Headline Length Box Plot")
fig_headline = px.box(filtered, x="source", y="headline_len", points="all", title="Headline Length per Article")
st.plotly_chart(fig_headline, use_container_width=True)

st.subheader("📝 Word Count Box Plot")
fig_word = px.box(filtered, x="source", y="word_count", points="all", title="Word Count per Article")
st.plotly_chart(fig_word, use_container_width=True)

st.subheader("📊 Headline Length vs. Word Count (Scatter)")
fig_scatter = px.scatter(
    filtered,
    x="word_count",
    y="headline_len",
    color="source",
    hover_data=["headline", "section"],
    title="Headline Length vs. Word Count"
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("🖼️ Image Count Distribution")
fig_img = px.histogram(filtered, x="num_images", color="source", nbins=15, barmode="group", title="Number of Images per Article")
st.plotly_chart(fig_img, use_container_width=True)

st.subheader("📢 Number of Ads per Article")
fig_ads = px.histogram(filtered, x="num_ads_est", color="source", nbins=10, barmode="group", title="Estimated Number of Ads per Article")
st.plotly_chart(fig_ads, use_container_width=True)

# 📚 Section Popularity Over Time
st.subheader("📚 Section Popularity Over Time")
fig_section_time = px.histogram(
    filtered,
    x="pub_date",
    color="section",
    nbins=40,
    title="Article Count by Section Over Time",
    labels={"pub_date": "Publication Date", "count": "Number of Articles"}
)
st.plotly_chart(fig_section_time, use_container_width=True)

# 🧮 Average Article Length by Section
st.subheader("🧮 Average Article Length by Section")
avg_lengths = (
    filtered.groupby("section")["word_count"]
    .mean()
    .reset_index()
    .sort_values(by="word_count", ascending=False)
)
fig_avg_length = px.bar(
    avg_lengths,
    x="section",
    y="word_count",
    title="Average Word Count per Section",
    labels={"word_count": "Average Word Count"},
)
st.plotly_chart(fig_avg_length, use_container_width=True)

# Display data preview
st.subheader("📄 Filtered Article Data")
st.dataframe(filtered[["pub_date", "source", "section", "headline", "headline_len", "word_count", "num_images", "num_ads_est"]], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data sourced from the Baltimore Banner and Capitol Gazette.")
