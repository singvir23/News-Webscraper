import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import datetime

# Streamlit config
st.set_page_config(page_title="News Visualizer", layout="wide")
st.title("Maryland News Articles Visualization Dashboard")
st.markdown(
    "This dashboard visualizes articles from the Capitol Gazette, Hyattsville Wire, and Baltimore Banner. Use the filters to explore different sources and date ranges.")
# Load data from PostgreSQL
@st.cache_data(ttl=600)
def load_data():
    engine = create_engine(
        "postgresql+psycopg2://scraperdb_owner:npg_mbyWDf3q5rFp@ep-still-snowflake-a4l5opga-pooler.us-east-1.aws.neon.tech/scraperdb?sslmode=require"
    )
    cg = pd.read_sql_query("SELECT * FROM capitol_gazette;", engine)
    hw = pd.read_sql_query("SELECT * FROM hyattsville_wire;", engine)
    bb = pd.read_sql_query("SELECT * FROM baltimore_banner;", engine)
    print(f"Loaded {len(cg)} Capitol Gazette articles, {len(hw)} Hyattsville Wire articles, and {len(bb)} Baltimore Banner articles.")
    cg["source"] = "Capital Gazette"
    hw["source"] = "Hyattsville Wire"
    cg = cg[cg['word_count'] > 30]  # remove paywalled articles from CG
    bb["source"] = "Baltimore Banner"
    # Remove timezone from pub_date if present
    if hasattr(hw["pub_date"], 'dt'):
        hw["pub_date"] = hw["pub_date"].dt.tz_localize(None)
    if hasattr(bb["pub_date"], 'dt'):
        bb["pub_date"] = bb["pub_date"].dt.tz_localize(None)
    df = pd.concat([cg, hw, bb], ignore_index=True)
    df = df.dropna(subset=["headline", "pub_date"])
    df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")
    df = df.dropna(subset=["pub_date"])
    df = df[(df["headline_len"] > 0) & (df["word_count"] > 0)]
    return df

df = load_data()

#remove outliers
df = df[df["word_count"] < 5000]  # Remove articles with excessive word count
print(f"HW articles after filtering: {len(df[df['source'] == 'Hyattsville Wire'])}")

# Sidebar filters
st.sidebar.header("🔍 Filters")

sources = st.sidebar.multiselect(
    "Select News Sources",
    options=df["source"].unique(),
    default=df["source"].unique()
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
    (df["pub_date"] >= pd.to_datetime(date_range[0])) &
    (df["pub_date"] <= pd.to_datetime(date_range[1]))
]

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

st.subheader("🔗 Number of Links per Article by Source")
fig_links = px.box(
    filtered,
    x="source",
    y="num_links",
    points="all",
    title="Distribution of Links per Article by News Source",
)
st.plotly_chart(fig_links, use_container_width=True)

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
# NEEDS TO BE SEPERATED OUT (Have one for bamtimore banner and capital gazette, and one for hyattsville wire)
# since they have different section names
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



# Visualization: Number of articles by day of the week, separated by source
st.subheader("📆 Articles by Day of the Week (by Source)")
filtered["weekday"] = filtered["pub_date"].dt.day_name()
fig_weekday_source = px.histogram(
    filtered,
    x="weekday",
    color="source",
    category_orders={"weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
    title="Number of Articles by Day of the Week (by Source)",
    labels={"weekday": "Day of Week", "count": "Number of Articles"},
    barmode="group"
)
st.plotly_chart(fig_weekday_source, use_container_width=True)

# Display data preview
st.subheader("📄 Filtered Article Data")
st.dataframe(filtered[["pub_date", "source", "section", "headline", "headline_len", "word_count", "num_images", "num_ads_est"]], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data sourced from the Capitol Gazette, the Baltimore Banner, and the Hyattsville Wire.")
