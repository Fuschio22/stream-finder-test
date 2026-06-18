from playwright.sync_api import sync_playwright

def main():
    stream_urls = []

    def handle_response(response):
        url = response.url
        # Cattura QUALSIASI flusso m3u8 (più flessibile)
        if ".m3u8" in url:
            stream_urls.append(url)
            print(f"🎯 Intercettato: {url}")

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
            page.wait_for_timeout(20000)  # Aumentato a 20 secondi
        except Exception as e:
            print(f"⚠️ Errore di caricamento: {e}")
        
        browser.close()

    if stream_urls:
        # Filtra per trovare il flusso migliore (quello con "cielo" o "TACT" nel nome)
        best_url = None
        for url in stream_urls:
            if "cielo" in url.lower() or "TACT" in url:
                best_url = url
                break
        
        # Se non trova quello specifico, usa il primo trovato
        if not best_url and stream_urls:
            best_url = stream_urls[0]
        
        print(f"\n✅ STREAM TROVATO:\n{best_url}")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write(best_url + "\n")
    else:
        print("\n❌ Nessun stream trovato. Riproverò al prossimo ciclo.")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write("Nessun stream trovato. Riprovo al prossimo aggiornamento.\n")

if __name__ == "__main__":
    main()
