import json
import httpx
from langchain_core.tools import tool
from src.core.setting import settings


@tool
async def web_search(query: str) -> str:
    """Search the web for current information about any topic."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": settings.GOOGLE_API_KEY,
                    "cx": settings.GOOGLE_CSE_ID,
                    "q": query,
                    "num": 5,
                },
            )
            response.raise_for_status()
            data = response.json()
        return json.dumps(
            [
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
                for item in data.get("items", [])
            ],
            indent=2,
        )
    except Exception as e:
        print("tool failed")
        return json.dumps(
            [
                {
                    "title": "Error",
                    "url": "https://www.google.com/",
                    "snippet": "Our tool has been down for some reason plz try again later.",
                }
            ]
        )

@tool
async def http_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    json_body: dict | None = None,
) -> str:
    """Make an HTTP request to an external API and return the response body."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.request(
            method=method.upper(),
            url=url,
            headers=headers or {},
            json=json_body,
        )
        return response.text
