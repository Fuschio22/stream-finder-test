from playwright.sync_api import sync_playwright

interesting = []

KEYWORDS = [
    "token",
    "auth",
    "play",
    "playback",
    "stream",
    "video",
    "live",
    "channel",
    "manifest",
    "session",
    "api"
]

def handle_response(response):
    url = response.url.lower()

    if any(k in url for k in KEYWORDS):
        interesting.append(f"{response.status} | {response.url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        user_agent="Mozilla/5.0"
    )

    page.on("response", handle_response)

    page.goto(
        "https://www.cielotv.it/streaming",
        wait_until="networkidle",
        timeout=60000
    )

    page.wait_for_timeout(20000)

    browser.close()

print("\n=== RICHIESTE INTERESSANTI ===\n")

for item in sorted(set(interesting)):
    print(item)
