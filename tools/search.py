import re
from typing import List, Tuple, Union
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
import httpx
from selectolax.parser import HTMLParser
import asyncio
from utils.chroma_client import search_with_semantic_cache, generate_new_result
from utils.config import service_settings as settings

from utils.logger import CustomLogger

logger = CustomLogger(__name__)


class SearchInput(BaseModel):
    search_query: str = Field(description="Search query to look up")


async def search_tool(search_query: str) -> Union[List[str], str]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": search_query,
        "key": settings.SEARCH_API_KEY,
        "cx": settings.CX,
        "num": 5
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            items = result.get("items", [])
            if not items:
                return []
            urls = [item['link'] for item in items]
            return urls if isinstance(urls, list) else []
    except Exception as e:
        return f"Search failed: {str(e)}"


def clean_html_text(node) -> str:
    """Extracts only visible, meaningful text from a Selectolax HTML tree."""
    text_parts = []
    for el in node.iter():
        # Skip garbage tags
        if el.tag in {"script", "style", "meta", "link", "head", "noscript"}:
            continue
        text = el.text(strip=True)
        if not text:
            continue
        # Skip CSS class or variable dump
        if re.match(r"^\..*{|^--|^@media|{.*}", text):  # style declarations or media queries
            continue
        # Skip over anything resembling raw CSS
        if ":" in text and ";" in text and re.search(r"--|font|margin|padding|color", text):
            continue
        if len(text) < 3:
            continue  # skip noise like "." or single chars
        # Keep legitimate content with spacing
        if el.tag in {"h1", "h2", "h3", "p", "li", "article", "section"}:
            text_parts.append("\n" + text)
        else:
            text_parts.append(text)

    joined = " ".join(text_parts)
    cleaned = re.sub(r"\s+", " ", joined).strip()

    lines = re.split(r"(?<=[.!?])\s+", cleaned)
    return "\n".join(line for line in lines if len(line.strip()) > 5)


async def extract_html(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch {url}: {e.response.status_code} | {e.response.reason_phrase}")
            return "Error fetching page"


def extract_main_content(tree: HTMLParser) -> str:
    for selector in ["article", "main", "section", "div.content", "div#main"]:
        node = tree.css_first(selector)
        if node:
            return clean_html_text(node)
    return clean_html_text(tree.body)


def extract_tables(tree: HTMLParser) -> List[dict]:
    logger.debug("Extracting tables from HTML tree")
    tables = []
    for table in tree.css("table"):
        headers = [th.text(strip=True) for th in table.css("th")]
        rows = []
        for tr in table.css("tr"):
            cells = [td.text(strip=True) for td in tr.css("td")]
            if cells:
                rows.append(cells)
        tables.append({"headers": headers, "rows": rows})
    return tables


async def parse_page(url: str) -> Tuple[str, List[dict]]:
    logger.info(f"Parsing page: {url}")
    html = await extract_html(url)
    tree = HTMLParser(html)
    main_text = extract_main_content(tree)
    tables = extract_tables(tree)
    return main_text, tables


async def parse_multiple_pages(urls: List[str]) -> List[Tuple[str, List[dict]]]:
    logger.info("Parsing multiple pages")
    tasks = [parse_page(url) for url in urls]
    return await asyncio.gather(*tasks)


async def web_search_tool(search_input: str) -> List[Tuple[str, List[dict]]]:
    logger.info(f"Performing web search tool for input: {search_input}")
    cached_query = await search_with_semantic_cache(search_input)
    if cached_query:
        logger.debug("Returning cached query result")
        return cached_query
    urls = await search_tool(search_input)
    if not urls:
        return []
    output = await parse_multiple_pages(urls)
    final_result = []
    for idx, (main_text, tables) in enumerate(output):
        final_result.append(
            {
                "url_index": urls[idx],
                "content": main_text,
                "tables": [
                    {
                        "headers": table["headers"],
                        "rows": table["rows"]
                    }
                    for table in tables
                ]
            }
        )
    await generate_new_result(search_input, str(final_result))
    logger.debug("Added new result to semantic cache")
    return final_result


def sync_web_search_tool(search_input: str) -> List[Tuple[str, List[dict]]]:
    """Synchronous wrapper for the async web search tool."""
    return asyncio.run(web_search_tool(search_input))


search_api_tool = Tool(
    name="web_search_tool",
    func=sync_web_search_tool,
    description=(
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query."        
        "Returns a list of structured results including cleaned content and any tables found."
    ),
    args_schema=SearchInput,
)
