import xml.etree.ElementTree as ET
import random
import re
import pandas as pd
from supabase_utils import insert_page, insert_quote, get_all_pages, get_all_quotes, insert_provisional_quote
from openRouterClient import fetch_chat_completion
from bs4 import BeautifulSoup, Comment
import html

# Constants
NAMESPACE = "{http://www.mediawiki.org/xml/export-0.11/}"
ROW_LIMIT = 10
QUOTE_LIMIT = 20
QUOTE_MIN_LENGTH = 2
QUOTE_MAX_LENGTH = 200
csv_file = 'data\\topviews-2024.csv'
xml_file = "data\\enwikiquote-latest-pages-articles.xml"
filter_model = "qwen/qwen-2.5-7b-instruct"
formatter_model = "qwen/qwen-2.5-7b-instruct"
extractor_model = "deepseek/deepseek-r1:free"
filter_prompt_body = ""
formatter_prompt_body = ""
extractor_prompt_body = ""

# add the results of multiple csv files together: add rows with the same page name together
def add_csv_files(csv_files):
    """Add the results of multiple CSV files together."""
    df = pd.concat([pd.read_csv(file) for file in csv_files])
    return df.groupby('Page').sum().reset_index()

def get_page_names_from_csv():
    """Read the first column of the CSV file and return page names as a list."""
    df = pd.read_csv(csv_file)
    
    return df.iloc[:ROW_LIMIT, 0].tolist()
    # return df.iloc[:, 0].tolist()

def parse_xml():
    """Load and parse the XML dump."""
    tree = ET.parse(xml_file)
    return tree.getroot()


def extract_and_insert_matching_pages(page_names):
    """Extract pages from the XML that match CSV rows and insert them into the database
    using the 'insert_page' function."""
    root = parse_xml()

    """Extract pages from the XML that match CSV rows."""
    all_pages = root.findall(f"{NAMESPACE}page")
    matched_pages = []

    for page in all_pages:
        ns = page.find(f"{NAMESPACE}ns").text
        if ns != "0":  # Skip non-article pages
            continue

        title = page.find(f"{NAMESPACE}title").text
        if title in page_names:
            matched_pages.append(title)
            # insert_page(title)  # ✅ Now calling from supabase_utils.py

    return matched_pages

def extract_and_insert_matching_pages_dict(page_dict):
    """Extract pages from the XML that match CSV rows and insert them into the database
    using the 'insert_page' function."""
    root = parse_xml()

    """Extract pages from the XML that match CSV rows."""
    all_pages = root.findall(f"{NAMESPACE}page")
    matched_pages = []

    page_names = []
    for key, values in page_dict.items():
        page_names.append(key)

    for page in all_pages:
        ns = page.find(f"{NAMESPACE}ns").text
        if ns != "0":  # Skip non-article pages
            continue

        title = page.find(f"{NAMESPACE}title").text
        if title in page_names:
            matched_pages.append(title)
            # print insert_page(title, page_dict[title][0], page_dict[title][1], page_dict[title][2])
            # print(f"Page: {title}, Values: {page_dict[title]}")
            insert_page(title, page_dict[title][0], page_dict[title][1], page_dict[title][2])  # ✅ Now calling from supabase_utils.py

    return matched_pages


def clean_text_regex(text):
    """Clean and transform text using regex."""

    # [[ArticleName]] → ArticleName
    # Example: [[Moon]] → Moon
    direct_link_pattern = re.compile(r"\[\[([^|]+?)\]\]", re.MULTILINE)

    # [[w:Article|Label]] → Label (Article)
    # Example: [[w:Moon|The Moon]] → The Moon (Moon)
    interwiki_link_pattern = re.compile(r"\[\[w:([^|]+?)\|([^|]+?)\]\]")

    # [[Article|Label]] → Label (Article)
    # Example: [[Earth|Planet Earth]] → Planet Earth (Earth)
    alternative_link_pattern = re.compile(r"\[\[([^|]+?)\|([^|]+?)\]\]")

    # [https://url.com Label] → Label (https://url.com)
    # Example: [https://example.com Site] → Site (https://example.com)
    hyperlink_pattern = re.compile(r"\[([a-zA-Z]+:\/\/[^\s]+)\s+(.+?)\]")

    # Remove multi-line citation templates
    # Example: {{citation | title=Example | url=... }} → flattened to single line
    citation_block_pattern = re.compile(r"({{citation[\s\S]*?}}$)", re.MULTILINE)

    # Remove anchor templates entirely
    # Example: {{anchor|SomeID}} → (removed)
    anchor_template_pattern = re.compile(r"{{anchor\|.+?}}")

    # {{w|Something}} → (Something)
    # Example: {{w|Universe}} → (Universe)
    interwiki_template_pattern = re.compile(r"{{w\|(.+?)}}")

    # :'''Speaker''': or '''Speaker''': → **Speaker**:
    # Example: :'''Interviewer''': → **Interviewer**:
    dialogue_bold_speaker_pattern = re.compile(r"^:?\s*'''(.*?)'''\s*:")

    # Remove (wikipedia:Something)
    # Example: (wikipedia:Hiding) → (removed)
    wikipedia_link_pattern = re.compile(r"\(wikipedia:[^)]+?\)")

    # Apply substitutions
    text = direct_link_pattern.sub(r"\1", text)
    text = interwiki_link_pattern.sub(r"\2 (\1)", text)
    text = alternative_link_pattern.sub(r"\2 (\1)", text)
    text = hyperlink_pattern.sub(r"\2 (\1)", text)
    text = citation_block_pattern.sub(lambda match: " ".join(map(str.strip, match.group(0).splitlines())), text)
    text = anchor_template_pattern.sub("", text)
    text = interwiki_template_pattern.sub(r"(\1)", text)
    text = dialogue_bold_speaker_pattern.sub(r"**\1**:", text)
    text = wikipedia_link_pattern.sub("", text)

    return text



def clean_html_preserve_br(input_html):
    """Clean HTML and preserve <br>"""
    soup = BeautifulSoup(input_html, "html.parser")

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Replace <br> tags with a newline
    for br in soup.find_all("br"):
        br.replace_with("\n")

    # Get text content
    text = soup.get_text()

    # Unescape HTML entities (e.g., &nbsp;)
    text = html.unescape(text)

    # Normalize whitespace but keep newlines
    text = re.sub(r'[ \t]+', ' ', text)        # Remove extra spaces
    text = re.sub(r'\s*\n\s*', '\n', text)     # Clean up line breaks
    text = text.strip()

    return text

def prepare_metadata_and_root():
    with open("prompts/prompt-1-filter.md", "r", encoding="utf-8") as file:
        filter_prompt_body = file.read()
    with open("prompts/prompt-2-formatter.md", "r", encoding="utf-8") as file:
        formatter_prompt_body = file.read()
    with open("prompts/prompt-3-extractor.md", "r", encoding="utf-8") as file:
        extractor_prompt_body = file.read()

    root = parse_xml()
    # page_table_rows = get_all_pages()[:ROW_LIMIT]
    page_table_rows = get_all_pages()[:]
    page_names = [row['page_name'] for row in page_table_rows]
    page_id_map = {row['page_name']: row['id'] for row in page_table_rows}

    return filter_prompt_body, formatter_prompt_body, extractor_prompt_body, root, page_names, page_id_map


def process_page_quotes(root, page_names, page_id_map):
    all_pages = root.findall(f"{NAMESPACE}page")
    pages_quote_data = {name: [] for name in page_names}

    for page in all_pages:
        ns = page.find(f"{NAMESPACE}ns").text
        if ns != "0":
            continue

        title = page.find(f"{NAMESPACE}title").text
        if title not in page_names:
            continue

        if re.match(r"List of", title, re.IGNORECASE):
            continue

        text = page.find(f"{NAMESPACE}revision").find(f"{NAMESPACE}text").text
        if not text:
            continue

        page_id = page_id_map[title]
        text = clean_html_preserve_br(text)
        text = clean_text_regex(text)

        lines = text.splitlines()
        lines_iter = iter(lines)
        hierarchy = []

        for line in lines_iter:
            # if invalid heading, reset hierarchy
            if re.match(r"^\s*==\s*(Cast|Notes|References|See also|External links)\s*==\s*$", line, re.IGNORECASE):
                hierarchy = []
                continue

            heading_match = re.match(r"^(=+)\s*(?!Cast|Notes|References|See also|External links)([^=]+?)\s*=+$", line.strip(), re.IGNORECASE)
            if heading_match:
                heading_level = len(heading_match.group(1))  # Number of '=' determines nesting level
                heading_title = heading_match.group(2).strip()

                # Adjust hierarchy stack
                # If current heading is less nested, pop until we match level
                # print(f"Heading: {heading_title}, Level: {heading_level}, Hierarchy: {hierarchy}, Pop: {hierarchy[-1] if hierarchy else 'None'}")
                while len(hierarchy) >= heading_level - 1 and hierarchy:
                    # print(f"Pop: {hierarchy[-1]}")
                    hierarchy.pop()
                hierarchy.append(heading_title)
                continue


            quote_match = re.match(r"^([*])\s*([^*].+)$", line)
            if quote_match and QUOTE_MIN_LENGTH < len(quote_match.group(2).split()) < QUOTE_MAX_LENGTH:
                quote = quote_match.group(2).strip()
                bold_text = re.findall(r"'''(.*?)'''", quote)

                if not bold_text:
                    continue
                # if re.match(r"^'''[^']*'''\s*:", quote_context) and len(bold_text) == 1:
                #     continue

                # filter_prompt = f"{filter_prompt_body}\nHere is the quote you need to extract:\n${quote_context}"
                # is_quotable = fetch_chat_completion(filter_model, filter_prompt).strip() == "Quotable"
                # if not is_quotable:
                #     continue

                hierarchy_str = " > ".join(hierarchy)
                quote_info = []

                while True:
                    next_line = next(lines_iter, None)
                    if next_line is None or not re.match(r"(^[*]{2,})\s*([^*].+)$", next_line):
                        break
                    match = re.match(r"(^[*]{2,})\s*([^*].+)$", next_line)
                    if match:
                        info = match.group(2).strip()
                        if len(info) > 100:
                            info = info[:100] + "..."
                        quote_info.append(info)

                quote_info_str = "; ".join(quote_info[:3])
                pages_quote_data[title].append((title, page_id, quote, hierarchy_str, quote_info_str))

        # random.shuffle(pages_quote_data[title])
    return pages_quote_data


def store_quotes(pages_quote_data):
    # print(f"Number of pages: {len(pages_quote_data)}")
    # return
    for page_name, quotes_data in pages_quote_data.items():
        for quote_data in quotes_data[:QUOTE_LIMIT]:
            # print("=" * 40)
            # print(f"Quote data: {quote_data}")
            insert_provisional_quote(*(quote_data[1:]))

def extract_quotes():
    filter_prompt_body, formatter_prompt_body, extractor_prompt_body, root, page_names, page_id_map = prepare_metadata_and_root()
    pages_quote_data = process_page_quotes(root, page_names, page_id_map)
    store_quotes(pages_quote_data)


def print_random_quotes(page_names, pages_quote_data):
    """Print 50 random quotes per page."""
    for page_name in page_names:
        quotes = pages_quote_data.get(page_name, [])
        if quotes:
            sample = random.sample(quotes, min(len(quotes), QUOTE_LIMIT))
            print(f"Page: {page_name}")
            print(f"Quotes: {sample}")
            print("--------------------------------------------------")

# # retrieve all words from a single page
# def get_page_words(page_name):
#     """Retrieve all words from a single page."""
#     quotes = get_all_quotes(page_name)  # ✅ Now calling from supabase_utils.py
#     return [quote['quote'] for quote in quotes]