from bs4 import BeautifulSoup, Comment
import html
import re

def clean_html_preserve_br(input_html):
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

# Example usage
raw_html = """
<p>Torg: My lord, the ship appears to be <!-- clearly --> deserted.</p>
Kruge: How can that be? They're (wikipedia:Hiding) hiding!
<b>Torg:</b> Yes,&nbsp;sir. But the bridge is run by <i>computer</i>. It is the only thing speaking.<br>
Kruge: Speaking? Let me hear.
"""

cleaned = clean_html_preserve_br(raw_html)
print(cleaned)
