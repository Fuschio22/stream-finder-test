from playwright.sync_api import sync_playwright

def main():
    stream_url = None

    def handle_response(response):
        nonlocal stream_url
        url = response.url
        # Intercetta i flussi m3u8. Ho mantenuto il tuo filtro "cieloweb"
        if ".m3u8" in url and "cieloweb" in url:
            stream_url = url
            print(f"🎯 Intercettato: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Uso un User-Agent realistico per sembrare un browser Chrome normale
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.on("response", handle_response)

        try:
            print("🌐 Caricamento della pagina in corso...")
            page.goto("https://www.cielotv.it/streaming", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(15000) # Attendo 15s per dare al player il tempo di caricare lo stream
        except Exception as e:
            print(f"⚠️ Errore di caricamento: {e}")
        
        browser.close()

    if stream_url:
        print(f"\n✅ STREAM TROVATO:\n{stream_url}")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write(stream_url + "\n")
    else:
        print("\n❌ Nessun stream trovato. Riproverò al prossimo ciclo.")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write("Nessun stream trovato. Riprovo al prossimo aggiornamento.\n")

if __name__ == "__main__":
    main()
