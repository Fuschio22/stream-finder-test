from playwright.sync_api import sync_playwright
import re

def main():
    stream_urls = []

    def handle_response(response):
        url = response.url
        if ".m3u8" in url:
            stream_urls.append(url)
            print(f"🎯 Flusso trovato: {url[:150]}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.on("response", handle_response)

        try:
            print("🌐 Caricamento pagina...")
            page.goto("https://www.cielotv.it/streaming", wait_until="networkidle", timeout=60000)
            
            # ATTESA INIZIALE
            page.wait_for_timeout(3000)
            
            # 1. ACCETTA COOKIE
            print("🍪 Accettazione cookie...")
            try:
                # Cerca pulsanti di accettazione
                accept_selectors = [
                    'button:has-text("Accetta")',
                    'button:has-text("Accept")',
                    'button:has-text("OK")',
                    'button:has-text("Consenti")',
                    '[id*="accept"]',
                    '[class*="accept"]',
                    '.fc-cta-consent',
                    '#onetrust-accept-btn-handler'
                ]
                
                for selector in accept_selectors:
                    try:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            print(f"✅ Cookie accettati con: {selector}")
                            page.wait_for_timeout(2000)
                            break
                    except:
                        continue
                
                # Fallback: imposta cookie manualmente
                page.evaluate("""
                    document.cookie = "consent=true; path=/; max-age=31536000";
                    document.cookie = "gdpr_consent=given; path=/; max-age=31536000";
                """)
            except Exception as e:
                print(f"⚠️ Errore cookie: {e}")
            
            # 2. CLICCA SUL PLAYER
            print("▶️ Attivazione player...")
            try:
                play_selectors = [
                    'video',
                    '[class*="player"]',
                    '[id*="player"]',
                    'button:has-text("Play")',
                    '[aria-label*="Play"]',
                    '.jw-icon-display',
                    '.video-js',
                    '#video-player',
                    '[class*="play-button"]'
                ]
                
                for selector in play_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=2000):
                            elem.click()
                            print(f"✅ Player attivato con: {selector}")
                            page.wait_for_timeout(3000)
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Errore player: {e}")
            
            # 3. ATTESA FINALE per caricamento stream
            print("⏳ Attesa caricamento stream...")
            page.wait_for_timeout(15000)
            
            # 4. CERCA NEL CODICE SORGENTE (fallback)
            print("🔎 Ricerca nel codice HTML...")
            content = page.content()
            m3u8_matches = re.findall(r'https?://[^\s"\']+\.m3u8[^\s"\']*', content)
            if m3u8_matches:
                print(f"🎯 Trovati {len(m3u8_matches)} URL nel codice")
                for match in m3u8_matches[:5]:
                    print(f"   - {match[:150]}")
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
