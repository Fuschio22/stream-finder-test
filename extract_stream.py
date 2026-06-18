from playwright.sync_api import sync_playwright
import re

def main():
    stream_urls = []

    def handle_response(response):
        url = response.url
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
            
            # Aspetta che la pagina si carichi
            page.wait_for_timeout(3000)
            
            # GESTIONE COOKIE CONSENT - Prova diversi metodi
            print("🍪 Gestione cookie consent...")
            
            # Metodo 1: Cerca e clicca il pulsante "Accetta" o "Accetta tutti"
            try:
                accept_buttons = page.locator('button:has-text("Accetta"), button:has-text("Accept"), button:has-text("consenti"), [id*="accept"], [class*="accept"]')
                if accept_buttons.count() > 0:
                    accept_buttons.first.click()
                    print("✅ Cookie accettati (metodo 1)")
                    page.wait_for_timeout(2000)
            except Exception as e:
                print(f"⚠️ Metodo 1 fallito: {e}")
            
            # Metodo 2: Inietta JavaScript per accettare automaticamente
            try:
                page.evaluate("""
                    // Prova a trovare e cliccare pulsanti di accettazione
                    const buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        const text = btn.textContent.toLowerCase();
                        if (text.includes('accetta') || text.includes('accept') || text.includes('consenti') || text.includes('ok')) {
                            btn.click();
                            break;
                        }
                    }
                    
                    // Prova a impostare cookie di consenso manualmente
                    document.cookie = "consent=true; path=/; max-age=31536000";
                    document.cookie = "gdpr_consent=given; path=/; max-age=31536000";
                """)
                print("✅ Cookie gestiti via JavaScript")
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"⚠️ Metodo 2 fallito: {e}")
            
            # Metodo 3: Cerca iframe del player e interagisci con esso
            print("🔍 Ricerca player video...")
            frames = page.frames
            print(f"📊 Trovati {len(frames)} frame")
            
            for frame in frames:
                try:
                    # Cerca pulsanti play o video in ogni frame
                    play_button = frame.locator('video, [class*="player"], [id*="player"], button:has-text("Play")')
                    if play_button.count() > 0:
                        print(f"✅ Trovato player in frame: {frame.url[:80]}")
                        # Prova a cliccare play
                        try:
                            play_button.first.click(timeout=3000)
                            print("▶️ Play cliccato")
                        except:
                            pass
                except:
                    pass
            
            # Aspetta che il player si carichi completamente
            print("⏳ Attesa caricamento player...")
            page.wait_for_timeout(20000)
            
            # Cerca anche nel codice sorgente
            print("🔎 Ricerca nel codice sorgente...")
            content = page.content()
            m3u8_matches = re.findall(r'https?://[^\s"\']+\.m3u8[^\s"\']*', content)
            if m3u8_matches:
                print(f"🎯 Trovati {len(m3u8_matches)} URL m3u8 nel codice")
                for match in m3u8_matches[:5]:
                    print(f"   - {match[:100]}")
                    if match not in stream_urls:
                        stream_urls.append(match)
            
        except Exception as e:
            print(f"⚠️ Errore: {e}")
        
        browser.close()

    if stream_urls:
        # Filtra per trovare il flusso migliore
        best_url = None
        for url in stream_urls:
            if any(keyword in url.lower() for keyword in ["cielo", "tact", "akamaized", "hlslive"]):
                best_url = url
                break
        
        if not best_url:
            best_url = stream_urls[0]
        
        print(f"\n✅ STREAM SALVATO:\n{best_url}")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write(best_url + "\n")
    else:
        print("\n❌ Nessun stream trovato.")
        with open("cielo.txt", "w", encoding="utf-8") as f:
            f.write("Nessun stream trovato.\n")

if __name__ == "__main__":
    main()
