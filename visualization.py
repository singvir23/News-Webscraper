import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Function to parse the data file
def parse_data(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as file:
        article = {}
        for line in file:
            line = line.strip()
            if line.startswith("Category:"):
                if article:  # Save previous article
                    data.append(article)
                    article = {}
                article["Category"] = line.split(": ", 1)[1]
            elif line.startswith("Title:"):
                article["Title"] = line.split(": ", 1)[1]
            elif line.startswith("URL:"):
                article["URL"] = line.split(": ", 1)[1]
            elif line.startswith("Date:"):
                date_str = line.split(": ", 1)[1]
                article["Date"] = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
            elif line.startswith("Word Count:"):
                article["Word Count"] = int(line.split(" ")[2])
            elif line.startswith("Images:"):
                article["Image Count"] = int(line.split(":")[1].split(" ")[1])
        if article:  # Save the last article
            data.append(article)
    return pd.DataFrame(data)

# Load data from both sources
cnn_data = parse_data("cnn_articles.txt")
fox_data = parse_data("fox_news_articles.txt")

# Add a source column
cnn_data["Source"] = "CNN"
fox_data["Source"] = "Fox News"

# Combine datasets
combined_data = pd.concat([cnn_data, fox_data])

# Visualization 1: Article count by category and source
plt.figure(figsize=(10, 6))
sns.countplot(data=combined_data, x="Category", hue="Source", palette="viridis")
plt.title("Article Count by Category and Source")
plt.xlabel("Category")
plt.ylabel("Number of Articles")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visualization 2: Average word count by category and source
plt.figure(figsize=(10, 6))
sns.barplot(data=combined_data, x="Category", y="Word Count", hue="Source", ci=None, palette="coolwarm")
plt.title("Average Word Count by Category and Source")
plt.xlabel("Category")
plt.ylabel("Average Word Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visualization 3: Articles published over time
plt.figure(figsize=(12, 6))
combined_data["Date"] = pd.to_datetime(combined_data["Date"])
sns.lineplot(data=combined_data, x="Date", hue="Source", estimator=None, y=combined_data.index, palette="Set2")
plt.title("Articles Published Over Time")
plt.xlabel("Date")
plt.ylabel("Cumulative Articles")
plt.legend(title="Source")
plt.tight_layout()
plt.show()

# Visualization 4: Image count distribution by source
plt.figure(figsize=(10, 6))
sns.boxplot(data=combined_data, x="Source", y="Image Count", palette="muted")
plt.title("Distribution of Image Counts by Source")
plt.xlabel("Source")
plt.ylabel("Image Count")
plt.tight_layout()
plt.show()
