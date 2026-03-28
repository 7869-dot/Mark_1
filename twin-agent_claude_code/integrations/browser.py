"""
integrations/browser.py

Browser integration using Playwright — three tools:
  - browser_fetch_page:    get the text content of any URL
  - browser_screenshot:    capture a screenshot (useful for debugging)
  - browser_search_web:    search the web via DuckDuckGo

The browser runs headless. No API keys needed.
First run requires: playwright install chromium
"""

from __future__ import annotations

from config.logging import get_logger
from integrations.base import BaseTool, ToolError

logger = get_logger(__name__)


class BrowserFetchPage(BaseTool):
    name = "browser_fetch_page"
    description = "Fetch and return the text content of any web page URL. Useful for reading articles, documentation, or any web content."
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Full URL to fetch (must start with http:// or https://)"},
            "max_chars": {"type": "integer", "description": "Max characters of content to return (default 3000)", "default": 3000},
        },
        "required": ["url"],
    }

    async def run(self, url: str, max_chars: int = 3000, **kwargs) -> str:
        if not url.startswith(("http://", "https://")):
            raise ToolError(f"Invalid URL: {url}. Must start with http:// or https://")

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ToolError("playwright not installed. Run: pip install playwright && playwright install chromium")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")

                # Extract visible text
                text = await page.evaluate("""() => {
                    const els = document.querySelectorAll('p, h1, h2, h3, h4, li, td, th');
                    return Array.from(els).map(e => e.innerText).join('\\n');
                }""")

                await browser.close()

            text = text.strip()[:max_chars]
            logger.debug("browser_fetch", url=url, chars=len(text))
            return f"Content from {url}:\n\n{text}" if text else f"No readable text found at {url}"

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to fetch {url}: {e}")


class BrowserSearchWeb(BaseTool):
    name = "browser_search_web"
    description = "Search the web using DuckDuckGo and return a list of results with titles and URLs."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "description": "Number of results to return (1-10)", "default": 5},
        },
        "required": ["query"],
    }

    async def run(self, query: str, max_results: int = 5, **kwargs) -> str:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ToolError("playwright not installed. Run: pip install playwright && playwright install chromium")

        try:
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(search_url, timeout=15000)

                results = await page.evaluate(f"""() => {{
                    const items = document.querySelectorAll('.result');
                    return Array.from(items).slice(0, {min(max_results, 10)}).map(item => {{
                        const title = item.querySelector('.result__title')?.innerText || '';
                        const url = item.querySelector('.result__url')?.innerText || '';
                        const snippet = item.querySelector('.result__snippet')?.innerText || '';
                        return {{ title, url, snippet }};
                    }});
                }}""")

                await browser.close()

            if not results:
                return f"No results found for: {query}"

            lines = []
            for r in results:
                lines.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}\n---")

            return f"Search results for '{query}':\n\n" + "\n".join(lines)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Web search failed: {e}")
