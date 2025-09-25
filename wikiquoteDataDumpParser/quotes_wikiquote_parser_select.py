import xml.etree.ElementTree as ET
import random
import re
import pandas as pd
from quotes_db_helper_supabase import insert_into_db
from pages_db_helper_supabase import get_all_rows

# main function
def main():
    print("Fetching all rows from the 'Pages' table...")
    page_table_rows = get_all_rows()
    # # print the rows
    # print(rows['page_name'])

    # Set quote limit
    quote_limit = 50

    # map page names to a list
    page_names = list(map(lambda x: x['page_name'], page_table_rows))
    page_id_map = {row['page_name']: row['id'] for row in page_table_rows}
    # print(page_names)

    # Read the first column of the CSV file
    df = pd.read_csv('data\\topviews-2024.csv')


    # Load and parse the XML dump
    tree = ET.parse("data\\enwikiquote-latest-pages-articles.xml")
    root = tree.getroot()

    namespace = "{http://www.mediawiki.org/xml/export-0.11/}"

    # Get all pages
    all_pages = root.findall(f"{namespace}page")
    

    # dictionary storing all the quote data from the selected pages
    pages_quote_data = {}
    # adding all the quote pages to the dictionary
    for name in page_names:
        pages_quote_data[name] = []

    # Select pages that match the CSV rows
    matched_pages = []
    for page in all_pages:

        # if quote_count >= quote_limit:
        #     continue

        ns = page.find(f"{namespace}ns").text  # Get namespace value
        if ns != "0":  # Skip non-article pages
            continue

        title = page.find(f"{namespace}title").text
        text = page.find(f"{namespace}revision").find(f"{namespace}text").text
        titlePattern = re.compile(r"List of", re.IGNORECASE)
        titleMatch = re.search(titlePattern, title)
        if titleMatch:
            continue
        if not text:
            continue
        
        # skip if the page is not in the selected pages
        if title not in page_names:
            continue


        page_id = page_id_map[title]
        # print(matched_pages)

        # Define regex patterns
        directLinkPattern = re.compile(r"\[\[([^|]+?)\]\]", re.MULTILINE)
        interwikiLinkPattern = re.compile(r"\[\[w:([^|]+?)\|([^|]+?)\]\]", re.MULTILINE)
        alternativeLinkPattern = re.compile(r"\[\[([^|]+?)\|([^|]+?)\]\]", re.MULTILINE)
        commentPattern = re.compile(r"<!--(.*?)-->", re.MULTILINE)
        hyperlinkPattern = re.compile(r"\[([a-zA-Z]+:\/\/[^\s]+)\s+(.+?)\]", re.MULTILINE)
        citationBlockPattern = re.compile(r"({{citation[\s\S]*?}}$)", re.MULTILINE)
        anchorTemplatePattern = re.compile(r"{{anchor\|.+?}}", re.MULTILINE)
        interwikiTemplatePattern = re.compile(r"{{w\|(.+?)}}", re.MULTILINE)

        # Apply transformations
        text = directLinkPattern.sub(r"\1", text)
        text = interwikiLinkPattern.sub(r"\2 (\1)", text)
        text = alternativeLinkPattern.sub(r"\2 (\1)", text)
        text = hyperlinkPattern.sub(r"\2 (\1)", text)
        text = citationBlockPattern.sub(lambda match: " ".join(map(str.strip, match.group(0).splitlines())), text)
        text = anchorTemplatePattern.sub("", text)
        text = interwikiTemplatePattern.sub(r"(\1)", text)

        # Process lines
        lines = text.splitlines()
        skippedHeadingsPattern = re.compile(r"^\s*==\s*(Notes|References|See also|External links|Disputed|Misattributed|Cast|Quotes About)\s*==\s*$", re.IGNORECASE)
        notSkippedHeadingsPattern = re.compile(r"^\s*==\s*(?!Notes|References|See also|External links|Disputed|Misattributed)([^=]+)==\s*$", re.IGNORECASE)

        currentHeading = None
        hierarchy = []

        lines_iter = iter(lines)

        for index, line in enumerate(lines_iter):
            if re.search(skippedHeadingsPattern, line):
                currentHeading = None
                hierarchy = []
                continue        

            if re.search(notSkippedHeadingsPattern, line):
                currentHeading = notSkippedHeadingsPattern.sub(r"\1", line).strip()
                hierarchy = [currentHeading]
                continue

            if currentHeading:
                currentSubHeadingPattern = re.compile(r"^([=]{3,})\s*([^=]+)[=]{3,}\s*$")
                quotePattern = re.compile(r"^([*])\s*([^*].+)$")
                quoteInfoPattern = re.compile(r"(^[*]{2,})\s*([^*].+)$")

                subHeadingMatch = currentSubHeadingPattern.match(line)
                quoteMatch = quotePattern.match(line)
                if subHeadingMatch:
                    subHeadingLevel = len(subHeadingMatch.group(1))
                    subHeading = subHeadingMatch.group(2).strip()
                    while len(hierarchy) + 2 > subHeadingLevel:
                        hierarchy.pop()
                    hierarchy.append(subHeading)

                if quoteMatch and len(quoteMatch.group(2)) < 200:
                    quote = quoteMatch.group(2).strip()

                    hierarchy_str = " > ".join(hierarchy)
                    quoteInfo = []
                    print("------------------------------")
                    print(f"Title: {title}")
                    print(f"Quote: {quote}")
                    print(f"Hierarchy: {' > '.join(hierarchy)}")

                    while lines:
                        next_line = next(lines_iter, None)
                        if next_line is None or not quoteInfoPattern.match(next_line):
                            break
                        # if len(quoteInfoPattern.match(next_line).group(2)) < 200:
                        #     quoteInfo.append(quoteInfoPattern.match(next_line).group(2).strip())

                        # Always capture quote info and trim to 150 characters
                        quoteInfo.append(quoteInfoPattern.match(next_line).group(2).strip()[:150])
                        print(f"Info: {quoteInfo}")

                    quoteInfoStr = ""
                    if quoteInfo:
                        quoteInfoStr = "; ".join(quoteInfo[:3])

                    # if quoteInfoStr:
                    #     print(f"Info: {quoteInfoStr}")

                    # # Call the helper function
                    # insert_into_db(page_id, title, quote, hierarchy_str, quoteInfoStr)
                    pages_quote_data[title].append((page_id, quote, hierarchy_str, quoteInfoStr))

    # printing 50 random quotes from each of the selected pages
    for page_name in page_names:
        print(f"Page: {page_name}")
        quotes = pages_quote_data[page_name]
        if len(quotes) < quote_limit:
            print(f"Quotes: {quotes}")
        else:
            print(f"Quotes: {random.sample(quotes, quote_limit)}")
        print("--------------------------------------------------")

    # adding the quotes to the database
    for page_name in page_names:
        quotes = pages_quote_data[page_name]
        for quote in quotes:
            # the asterisk is used to unpack the tuple
            insert_into_db(*quote)

main()