from playwright.sync_api import sync_playwright
import re

stream_url = None

def handle_response(response):
    global stream_url

    url = response.url

    if ".m3u8" in url and "cieloweb" in url:
        stream_url = url

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

if stream_url:
    print(f"TROVATO:\n{stream_url}")

    with open("cielo.txt", "w") as f:
        f.write(stream_url)
else:
    print("Nessun stream trovato")
