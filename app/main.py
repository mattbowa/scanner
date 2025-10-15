from fastapi import FastAPI
import httpx
import asyncio
from urllib.parse import quote_plus


app = FastAPI(title="Hello FastAPI")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


PROFILE_URLS = [
    "https://twitter.com/{u}",
    "https://www.facebook.com/{u}",
    "https://www.instagram.com/{u}",
    "https://github.com/{u}",
    "https://www.reddit.com/user/{u}",
    "https://www.linkedin.com/in/{u}",
    "https://www.pinterest.com/{u}",
    "https://www.tiktok.com/@{u}",
]

HEADERS = {
    "User-Agent": "Personal-Info-Scanner/1.0 (+https://example.com/your-contact)",
}

REQUEST_DELAY = 1.0


async def check_profile_urls(username: str, timeout: float = 8.0):
    found = []
    async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS, timeout=timeout) as client:
        for pattern in PROFILE_URLS:
            url = pattern.format(u=quote_plus(username))
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    found.append({"url": url, "status": r.status_code})
            except httpx.HTTPError:
                pass
            await asyncio.sleep(REQUEST_DELAY)

    return found


@app.get("/scan/{username}")
async def scan_username(username: str):
    results = await check_profile_urls(username)
    return {"username": username, "profiles": results}

