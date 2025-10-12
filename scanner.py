"""
quick-personal-info-finder.py
Proof-of-concept: searches username patterns on common sites and queries HaveIBeenPwned for email breaches.
Use responsibly and with your own accounts/data only.
"""

import requests
import time
import json
from urllib.parse import quote_plus
from tqdm import tqdm  # optional progress bar

# ========== CONFIG ==========
# Provide your identifiers here
NAMES = ["Mattias", "Matt B", "Matt B."]          # name variants (for search API)
USERNAMES = ["mattb", "mattiasb", "matt-b"]      # usernames you want to check
EMAILS = ["your.email@example.com"]              # emails to check with HIBP

# Site profile URL patterns (very limited sample)
PROFILE_URLS = [
    "https://twitter.com/{u}",
    "https://www.facebook.com/{u}",
    "https://www.instagram.com/{u}",
    "https://github.com/{u}",
    "https://www.reddit.com/user/{u}",
    "https://www.linkedin.com/in/{u}",  # usually won't work without canonical username
    "https://www.pinterest.com/{u}",
    "https://www.tiktok.com/@{u}",
]

# API keys (optional)
HIBP_API_KEY = ""   # get from https://haveibeenpwned.com/API/Key
GOOGLE_API_KEY = ""  # optional: Google Custom Search API key
GOOGLE_CX = ""       # optional: Custom Search Engine ID

# Request defaults
HEADERS = {
    "User-Agent": "Personal-Info-Scanner/1.0 (+https://example.com/your-contact)",
}
HIBP_HEADERS = {"hibp-api-key": HIBP_API_KEY, "User-Agent": HEADERS["User-Agent"]}

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests to avoid hammering


# ========== FUNCTIONS ==========
def check_profile_urls(username, timeout=8):
    """Try common profile URLs and return which ones look present (status 200)."""
    found = []
    for pattern in PROFILE_URLS:
        url = pattern.format(u=quote_plus(username))
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            if r.status_code == 200:
                found.append({"url": url, "status": r.status_code})
            # some platforms return 403, but still indicate existence differently; skip for now
        except requests.RequestException as e:
            # connection errors, timeouts etc.
            # You might want to log these separately
            pass
        time.sleep(REQUEST_DELAY)
    return found


def hibp_check_email(email):
    """Query HaveIBeenPwned for breaches for an email. Requires HIBP_API_KEY."""
    if not HIBP_API_KEY:
        return {"error": "no_hibp_api_key"}
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote_plus(email)}"
    try:
        r = requests.get(url, headers=HIBP_HEADERS, params={"truncateResponse": "false"}, timeout=10)
        if r.status_code == 200:
            # returns JSON list of breaches
            return {"breaches": r.json()}
        elif r.status_code == 404:
            return {"breaches": []}  # not found in breaches
        else:
            return {"error": f"hibp_status_{r.status_code}", "text": r.text}
    except requests.RequestException as e:
        return {"error": "request_exception", "exception": str(e)}


def google_search(query, num=10):
    """Use Google Custom Search JSON API. Requires GOOGLE_API_KEY and GOOGLE_CX."""
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        return {"error": "no_google_api_key_or_cx"}
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CX, "q": query, "num": min(num,10)}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": "request_exception", "exception": str(e)}


# ========== MAIN ==========

def main():
    results = {
        "profiles": {},
        "hibp": {},
        "google": {},
    }

    print("== Checking username-based profile URLs ==")
    for u in tqdm(USERNAMES):
        results["profiles"][u] = check_profile_urls(u)

    # print("\n== Querying HaveIBeenPwned for provided emails ==")
    # for e in EMAILS:
    #     res = hibp_check_email(e)
    #     results["hibp"][e] = res
    #     time.sleep(REQUEST_DELAY)

    # print("\n== Small Google search on name variants (if API keys provided) ==")
    # for n in NAMES:
    #     gs = google_search(n, num=5)
    #     results["google"][n] = gs
    #     time.sleep(REQUEST_DELAY)

    # Save results
    with open("scan_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nScan complete. Results saved to scan_results.json")
    return results


if __name__ == "__main__":
    r = main()
