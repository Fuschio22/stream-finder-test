from playwright.sync_api import sync_playwright
import re

def main():
    stream_urls = []
    all_responses = []

    def handle_response(response):
        url = response.url
        all_responses.append(url)
        # Cattura QUALSIASI flusso video
        if any(ext in url.lower() for ext in [".m3u8", ".mpd", ".ts", "video", "stream", "hls", "dash"]):
            stream_urls.append(url)
            print(f"🎯 Flusso trovato: {url[:150]}")

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
            page.wait_for_timeout(5000)
            
            # GESTIONE COOKIE CONSENT
            print("🍪 Gestione cookie consent...")
            try:
                page.evaluate("""
                    const buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        const text = btn.textContent.toLowerCase();
                        if (text.includes('accetta') || text.includes('accept') || text.includes('consenti') || text.includes('ok')) {
                            btn.click();
                            break;
                        }
                    }
                    document.cookie = "consent=true; path=/; max-age=31536000";
                """)
                print("✅ Cookie gestiti")
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"⚠️ Errore cookie: {e}")
            
            # CERCA E CLICCA IL PLAYER
            print("▶️ Ricerca e click sul player...")
            try:
                # Cerca vari tipi di pulsanti play
                play_selectors = [
                    'video',
                    '[class*="player"]',
                    '[id*="player"]',
                    'button:has-text("Play")',
                    '[class*="play"]',
                    '[aria-label*="Play"]',
                    '.jw-icon-display',
                    '.video-js',
                    '#video-player'
                ]
                
                for selector in play_selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible(timeout=2000):
                            print(f"✅ Trovato elemento: {selector}")
                            element.click()
                            print("▶️ Click effettuato")
                            page.wait_for_timeout(3000)
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Errore click player: {e}")
            
            # ESPLORA TUTTI I FRAME (anche annidati)
            print("🔍 Esplorazione frame...")
            frames = page.frames
            print(f"📊 Trovati {len(frames)} frame")
            
            for i, frame in enumerate(frames):
                print(f"🔍 Frame {i}: {frame.url[:100]}")
                
                # Cerca video in ogni frame
                try:
                    video = frame.locator('video').first
                    if video.is_visible(timeout=2000):
                        print(f"  ▶️ Video trovato in frame {i}")
                        video.click()
                        page.wait_for_timeout(2000)
                except:
                    pass
            
            # ATTESA FINALE per caricamento stream
            print("⏳ Attesa finale per caricamento stream...")
            page.wait_for_timeout(20000)
            
            # RICERCA NEL CODICE SORGENTE
            print("🔎 Ricerca nel codice sorgente...")
            content = page.content()
            
            # Cerca URL m3u8 nel codice HTML
            m3u8_matches = re.findall(r'https?://[^\s"\']+\.m3u8[^\s"\']*', content)
            if m3u8_matches:
                print(f"🎯 Trovati {len(m3u8_matches)} URL m3u8 nel codice")
                for match in m3u8_matches[:10]:
                    print(f"   - {match[:150]}")
                    if match not in stream_urls:
                        stream_urls.append(match)
            
            # Cerca anche pattern più generici
            video_patterns = re.findall(r'https?://[^\s"\']+(?:video|stream|hls|dash|cielo|tact)[^\s"\']*', content, re.IGNORECASE)
            if video_patterns:
                print(f"🎯 Trovati {len(video_patterns)} pattern video nel codice")
                for match in video_patterns[:10]:
                    print(f"   - {match[:150]}")
                    if match not in stream_urls:
                        stream_urls.append(match)
            
        except Exception as e:
            print(f"⚠️ Errore: {e}")
        
        browser.close()

    # DEBUG COMPLETO
    print(f"\n📊 DEBUG COMPLETO:")
    print(f"   Totale response: {len(all_responses)}")
    print(f"   Totale stream URLs: {len(stream_urls)}")
    
    if len(all_responses) > 0:
        print(f"\n📋 TUTTE le response (prime 50):")
        for i, url in enumerate(all_responses[:50]):
            print(f"   {i+1}. {url[:150]}")

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
