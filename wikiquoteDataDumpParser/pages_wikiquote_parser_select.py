import xml.etree.ElementTree as ET
import random
import re
import pandas as pd
from pages_db_helper_supabase import insert_into_db

# main function
def main():
    # Read the first column of the CSV file
    df = pd.read_csv('data\\topviews-2024.csv')
    first_column = df.iloc[:, 0] # return the top 10: .head(10)

    # # Print the first column
    # print(first_column)

    # Load and parse the XML dump
    tree = ET.parse("data\\enwikiquote-latest-pages-articles.xml")
    root = tree.getroot()

    namespace = "{http://www.mediawiki.org/xml/export-0.11/}"

    # Get all pages
    all_pages = root.findall(f"{namespace}page")

    # Select pages that match the CSV rows
    matched_pages = []
    titles = []
    for page in all_pages:
        ns = page.find(f"{namespace}ns").text  # Get namespace value
        if ns != "0":  # Skip non-article pages
            continue

        title = page.find(f"{namespace}title").text
        # print("------------------------------")
        # print(f"Title: {title}")
        
        titles.append(title)
        
        # Only keep pages whose titles are in the top CSV rows
        if title in first_column.values:
            matched_pages.append(title)
            # Insert into Supabase database
            insert_into_db(title)

    # Print matched pages
    print(len(titles))
    print(matched_pages)

main()