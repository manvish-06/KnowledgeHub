import requests
import re
import logging
from urllib.parse import quote
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SEARCH_API = "https://en.wikipedia.org/w/api.php"
SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"


REQUEST_TIMEOUT = 10
MAX_LIST_LENGTH = 8
MAX_YEAR_COUNT = 5
MIN_LINE_LENGTH = 4
MIN_SECTION_LENGTH = 20
MIN_PARAGRAPH_LENGTH = 30

HEADERS = {
    "User-Agent": "KnowledgeHub/1.0 (Educational Project)"
}


session = requests.Session()
session.headers.update(HEADERS)

STOP_SECTIONS = {
    "References", "External links", "Further reading", "Bibliography",
    "See also", "Authority control", "Notes", "Footnotes", "Citations",
    "Awards", "Awards and nominations", "Filmography", "Discography"
}

IGNORE_LIST_ITEMS = {
    "Media from Commons", "Quotations from Wikiquote", "Data from Wikidata",
    "VIAF", "ISNI", "LCCN", "IMDb", "ORCID", "MusicBrainz", "GND", "SUDOC"
}

METADATA_WORDS = {
    "actor", "film producer", "years active", "born",
    "occupation", "spouse", "children", "website"
}

# ============================================
# SEARCH & DOWNLOAD
# ============================================

def get_article_summary(title):

    try:
        url = SUMMARY_API + quote(title)
        # Using session.get() leverages the pooled TCP connection and global headers
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception:
        logger.exception("KnowledgeHub Warning - Could not fetch summary for: %s", title)
        return None


def search_wikipedia(query):

    if not query:
        return []

    try:
        response = session.get(
            SEARCH_API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json"
            },
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        search_results = data.get("query", {}).get("search", [])
        results = []

        for item in search_results[:5]:
            title = item.get("title")
            if not title:
                continue

            page = get_article_summary(title)
            if not page:
                continue

            results.append({
                "title": page.get("title"),
                "summary": page.get("extract"),
                "image": page.get("thumbnail", {}).get("source"),
                "url": page.get("content_urls", {}).get("desktop", {}).get("page")
            })

        return results
        
    except Exception:
        logger.exception("KnowledgeHub Error in search_wikipedia")
        return []


def get_article_html(title):

    try:
        response = session.get(
            SEARCH_API,
            params={
                "action": "parse",
                "page": title,
                "prop": "text",
                "format": "json"
            },
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        if "parse" not in data:
            return None
            
        return data["parse"]["text"]["*"]
    except Exception:
        logger.exception("KnowledgeHub Error downloading article: %s", title)
        return None


# ============================================
# PARSING & EXTRACTION
# ============================================

def clean_heading(text):
    text = remove_citations(text)
    return normalize_whitespace(text)


def parse_wikipedia_html(html):

    if not html:
        return None
    return BeautifulSoup(html, "html.parser")


def extract_sections(soup):

    sections = []
    current_title = "Introduction"
    current_content = []

    for element in soup.find_all(["h2", "h3", "p", "ul"]):
        
        # Handle Headings
        if element.name in ["h2", "h3"]:
            raw_heading = element.get_text(" ", strip=True)
            heading = clean_heading(raw_heading)
            
            if heading in STOP_SECTIONS:
                if current_content:
                    sections.append({"title": current_title, "content": "\n\n".join(current_content)})
                break
                
            if current_content:
                sections.append({"title": current_title, "content": "\n\n".join(current_content)})
            
            current_title = heading
            current_content = []

        # Handle Paragraphs (Cleaned Immediately)
        elif element.name == "p":
            text = element.get_text(" ", strip=True)
            text = remove_citations(text)
            text = normalize_whitespace(text)
            
            if len(text) > MIN_PARAGRAPH_LENGTH:
                current_content.append(text)

        # Handle Bulleted Lists (Cleaned Immediately)
        elif element.name == "ul":
            items = []
            for li in element.find_all("li", recursive=False):
                item = li.get_text(" ", strip=True)
                item = remove_citations(item)
                item = normalize_whitespace(item)
                
                if not item or item in IGNORE_LIST_ITEMS or len(item) < MIN_LINE_LENGTH:
                    continue
                items.append(f"• {item}")
                
            if items:
                current_content.append("\n".join(items))

    if current_content:
        sections.append({"title": current_title, "content": "\n\n".join(current_content)})

    return sections


# ============================================
# REUSABLE TEXT CLEANING UTILITIES
# ============================================

def remove_citations(text):

    if not text:
        return ""
    return re.sub(r"\[[^\]]*\]", "", text)


def normalize_whitespace(text):

    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_short_lines(text):

    cleaned = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or len(line) < MIN_LINE_LENGTH:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def clean_lists(text):

    lines = text.split("\n")
    cleaned = []
    current_list = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("•"):
            current_list.append(stripped)
            continue

        if current_list:
            remove_list = False

            if len(current_list) > MAX_LIST_LENGTH:
                remove_list = True

            year_count = sum(1 for item in current_list if re.search(r"\b19\d{2}\b|\b20\d{2}\b", item))
            if year_count >= MAX_YEAR_COUNT:
                remove_list = True

            if not remove_list:
                cleaned.extend(current_list)
            
            current_list = []

        cleaned.append(line)

    if current_list:
        cleaned.extend(current_list)

    return "\n".join(cleaned)


# ============================================
# PIPELINE FORMATTERS
# ============================================

def clean_sections(sections):

    cleaned_sections = []
    seen_titles = set()
    
    for sec in sections:
        title = sec["title"]
        
        if title in seen_titles:
            continue
        seen_titles.add(title)
        
        content = sec["content"]
        content = remove_short_lines(content)
        content = clean_lists(content)
        content = normalize_whitespace(content)
        
        if len(content) > MIN_SECTION_LENGTH:
            cleaned_sections.append({
                "title": title,
                "content": content
            })
            
    return cleaned_sections


def format_sections(sections):

    formatted = []
    for sec in sections:
        if sec["title"] == "Introduction":
            formatted.append(sec["content"])
        else:
            formatted.append(f"## {sec['title']}\n\n{sec['content']}")
    return "\n\n".join(formatted)


def finalize_article(article):

    lines = article.split("\n")
    cleaned = []
    seen = set()

    for line in lines:
        line = line.strip()

        if not line:
            cleaned.append("")
            continue
        

        normalized_key = line.lower()
        if normalized_key in seen:
            continue
        seen.add(normalized_key)

        if len(line) < 80 and any(word in normalized_key for word in METADATA_WORDS):
            continue

        cleaned.append(line)

    article = "\n\n".join(cleaned)
    article = re.sub(r"\n{3,}", "\n\n", article)
    return article.strip()


def generate_summary(article):

    if not article:
        return ""

    paragraphs = [p.strip() for p in article.split("\n\n") if p.strip()]
    
    if not paragraphs:
        return ""

    summary = paragraphs[0]

    if len(summary) > 350:
        summary = summary[:350]
        last_period = summary.rfind(".")
        if last_period != -1:
            summary = summary[:last_period + 1]
        else:
            summary = summary.strip() + "..."

    return summary


# ============================================
# MAIN ORCHESTRATOR
# ============================================

def get_full_wikipedia_article(title):

    html = get_article_html(title)
    if not html:
        return ""
        
    soup = parse_wikipedia_html(html)
    if not soup:
        return ""
        
    raw_sections = extract_sections(soup)
    cleaned_sections = clean_sections(raw_sections)
    raw_markdown = format_sections(cleaned_sections)
    final_markdown = finalize_article(raw_markdown)
    
    return final_markdown


def build_article_context(title):
    """
    Downloads a live Wikipedia article and returns an ArticleContext object
    that can be used directly by the AI pipeline.
    """

    from .ai import ArticleContext

    article = get_full_wikipedia_article(title)

    if not article:
        return None

    return ArticleContext(
        title=title,
        content=article,
        source="wikipedia",
        entry=None,
    )

