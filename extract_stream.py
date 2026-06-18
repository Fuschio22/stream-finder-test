from playwright.sync_api import sync_playwright

def main():
    stream_urls = []

    def handle_response(response):
        url = response.url
        # Cattura QUALSIASI flusso m3u8 (senza filtri rigidi)
        if ".m3u8" in url:
            stream_urls.append(url)
            print(f"🎯 Flusso m3u8 trovato: {url[:200]}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.on("response", handle_response)

        try:
            print("🌐 Caricamento della pagina in corso...")
            page.goto("https://www.cielotv.it/streaming", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(15000)
        except Exception as e:
            print(f"⚠️ Errore di caricamento: {e}")
        
        browser.close()

    if stream_urls:
        # Mostra tutti i flussi trovati
        print(f"\n📊 Trovati {len(stream_urls)} flussi m3u8:")
        for i, url in enumerate(stream_urls, 1):
            print(f"  {i}. {url[:200]}")
        
        # Usa il primo flusso trovato (o cerca quello con "cielo" se presente)
        best_url = stream_urls[0]
        for url in stream_urls:
            if "cielo" in url.lower() or "tact" in url.lower():
                best_url = url
                break
        
        print(f"\n✅ STREAM SALVATO:\n{best_url}")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write(best_url + "\n")
    else:
        print("\n❌ Nessun flusso m3u8 trovato.")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write("Nessun stream trovato.\n")

if __name__ == "__main__":
    main()
