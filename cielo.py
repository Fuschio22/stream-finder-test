from playwright.sync_api import sync_playwright

found = set()

def handle_response(response):
    url = response.url

    if any(x in url.lower() for x in [
        ".m3u8",
        ".mpd",
        "manifest",
        "playlist",
        "master"
    ]):
        found.add(url)

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

    page.wait_for_timeout(15000)

    browser.close()

print("\n=== RISULTATI ===\n")

if found:
    for url in sorted(found):
        print(url)
else:
    print("Nessun flusso trovato")
