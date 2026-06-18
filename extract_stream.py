from playwright.sync_api import sync_playwright
import re

def main():
    stream_urls = []
    all_responses = []

    def handle_response(response):
        url = response.url
        all_responses.append(url)
        
        # Cattura QUALSIASI flusso m3u8 o mpd
        if ".m3u8" in url or ".mpd" in url:
            stream_urls.append(url)
            print(f"🎯 Flusso trovato: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        page.on("response", handle_response)

        try:
            print("🌐 Caricamento della pagina in corso...")
            page.goto("https://www.cielotv.it/streaming", wait_until="domcontentloaded", timeout=60000)
            
            # Aspetta che la pagina sia completamente caricata
            page.wait_for_timeout(5000)
            
            # Cerca iframe che potrebbero contenere il player
            frames = page.frames
            print(f"📊 Trovati {len(frames)} frame nella pagina")
            
            for i, frame in enumerate(frames):
                print(f"🔍 Frame {i}: {frame.url}")
                # Aspetta un po' per permettere il caricamento dei flussi in ogni frame
                page.wait_for_timeout(3000)
            
            # Aspetta ancora per dare tempo al player di caricarsi
            print("⏳ Attesa aggiuntiva per il caricamento del player...")
            page.wait_for_timeout(15000)
            
            # Prova anche a cercare il flusso nel codice sorgente della pagina
            print("🔎 Ricerca nel codice sorgente...")
            content = page.content()
            
            # Cerca URL m3u8 nel codice HTML
            m3u8_matches = re.findall(r'https?://[^\s"\']+\.m3u8[^\s"\']*', content)
            if m3u8_matches:
                print(f"🎯 Trovati {len(m3u8_matches)} URL m3u8 nel codice sorgente")
                for match in m3u8_matches[:5]:  # Mostra i primi 5
                    print(f"   - {match}")
                    if match not in stream_urls:
                        stream_urls.append(match)
            
        except Exception as e:
            print(f"⚠️ Errore di caricamento: {e}")
        
        browser.close()

    # Debug: mostra tutte le response catturate
    print(f"\n📊 Totale response catturate: {len(all_responses)}")
    if len(all_responses) > 0:
        print("📋 Ultime 10 response:")
        for url in all_responses[-10:]:
            print(f"   - {url[:100]}...")

    if stream_urls:
        # Filtra per trovare il flusso migliore
        best_url = None
        
        # Cerca prima URL con "cielo" o "TACT" o "akamaized"
        for url in stream_urls:
            if any(keyword in url.lower() for keyword in ["cielo", "tact", "akamaized", "hlslive"]):
                best_url = url
                print(f"✅ Trovato URL prioritario: {best_url}")
                break
        
        # Se non trova quello specifico, usa il primo trovato
        if not best_url and stream_urls:
            best_url = stream_urls[0]
            print(f"✅ Usando primo URL trovato: {best_url}")
        
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write(best_url + "\n")
        print(f"\n✅ STREAM SALVATO:\n{best_url}")
    else:
        print("\n❌ Nessun stream trovato. Riproverò al prossimo ciclo.")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write("Nessun stream trovato. Riprovo al prossimo aggiornamento.\n")

if __name__ == "__main__":
    main()
