import csv
import re
import os
from datetime import datetime

def parse_text_file(file_path):
    """
    Parse a text file containing article data and extract the structured information.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        list: List of dictionaries containing the parsed data
    """
    articles = []
    current_article = {}
    
    # Read the entire file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split the content by double newlines to separate articles
    article_blocks = re.split(r'\n\n+', content)
    
    for block in article_blocks:
        if not block.strip():
            continue
            
        # If the block starts with "Category:", it's a new article
        if block.strip().startswith("Category:"):
            if current_article:
                articles.append(current_article)
            current_article = {}
            
            # Process the current block
            lines = block.strip().split('\n')
            for line in lines:
                if line.startswith("Category:"):
                    current_article['Category'] = line.replace("Category:", "").strip()
                elif line.startswith("Title:"):
                    current_article['Title'] = line.replace("Title:", "").strip()
                elif line.startswith("URL:"):
                    current_article['URL'] = line.replace("URL:", "").strip()
                elif line.startswith("Date:"):
                    date_str = line.replace("Date:", "").strip()
                    current_article['Date'] = date_str
                elif line.startswith("Word Count:"):
                    word_count_match = re.search(r'(\d+)', line)
                    if word_count_match:
                        current_article['Word Count'] = int(word_count_match.group(1))
                    else:
                        current_article['Word Count'] = None
                elif line.startswith("Images:"):
                    images_match = re.search(r'(\d+)', line)
                    if images_match:
                        current_article['Images'] = int(images_match.group(1))
                    else:
                        current_article['Images'] = None
                    
                    # Extract image sizes if available
                    sizes_match = re.search(r'Sizes:\s+([^)]+)', line)
                    if sizes_match:
                        current_article['Image Sizes'] = sizes_match.group(1).strip()
                    else:
                        current_article['Image Sizes'] = None
    
    # Add the last article if it exists
    if current_article:
        articles.append(current_article)
        
    return articles

def save_to_csv(articles, output_file):
    """
    Save the parsed article data to a CSV file.
    
    Args:
        articles (list): List of dictionaries containing the article data
        output_file (str): Path to the output CSV file
    """
    if not articles:
        print("No articles found to save.")
        return
        
    # Determine the fieldnames from the first article
    fieldnames = list(articles[0].keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"Successfully saved {len(articles)} articles to {output_file}")

def main():
    """
    Main function to run the script.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert text file with article data to CSV.')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--output', '-o', default=None, help='Path to the output CSV file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return
    
    # If output file is not specified, use the input filename with .csv extension
    output_file = args.output if args.output else os.path.splitext(args.input_file)[0] + '.csv'
    
    # Parse the text file
    articles = parse_text_file(args.input_file)
    
    if articles:
        # Save to CSV
        save_to_csv(articles, output_file)
    else:
        print("No articles found in the input file.")

if __name__ == "__main__":
    main()