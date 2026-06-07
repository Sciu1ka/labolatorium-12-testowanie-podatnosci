#pozwala na asynchroniczne wykonywanie funckcji
import asyncio

#jako iż testowałem ten program na OWASP Juicy Shop jest to strona typu Single Page Aplication
#zatem nie możemy użyć zwyczajnych scraperów, tylko musimy zasymulować przęgladrke
#do tego używamy playwright, który ma funkcje działania asynchronicznego
from playwright.async_api import async_playwright
import urllib.parse

# CEL SKANU
TARGET_BASE = [
    "http://localhost:3000/#/"
    ] 

#SKRYPTY JAVASCRIPT
PAYLOADS = [
    "<script>alert(1)</script>",
    "<iframe src=\"javascript:alert(`xss`)\">",
    "<img src=x onerror=alert(1)>",
    "</script><script>alert(1)</script>"
]

#MIEJSCA GDZIE MOŻE WYSTĘPOWAĆ PODATNOŚĆ
SINKS = [
    "search?q=",
]

#funckja skanujące
async def xss_scan(context, payload, target):
    
    #enkodujemy nasz payload
    encoded_payload = urllib.parse.quote(payload)
    vulnerable = False

    #otwieramy nową strona w przeglądrace
    page = await context.new_page()
    
    #nasza funckja która zajmuje się wyskakującymi alertami
    async def handle_alert(dialog):
        nonlocal vulnerable
        if dialog.type == "alert":
            vulnerable = True
        await dialog.dismiss()
    
    #nasz nasłuchiwać aletrów
    page.on("dialog", handle_alert)

    try:
        #idziemy na strone testować podatność
        await page.goto(target+encoded_payload, wait_until="networkidle", timeout=5000)
        await asyncio.sleep(2)  # czekam przez chwile by cała strona się załadowała
    except Exception as e:
        print(f"Error during scanning: {e}")
    finally:
        #na koniec zamykamy strone
        await page.close()
    
    #zwracmy czy podatnosc działa i jakiego skryptu użyliśmy
    return vulnerable, payload if vulnerable else None

#główna funcja asynchroniczna
async def main():
    async with async_playwright() as p:
        #otwiramy przeglądarke bez okna
        browser = await p.chromium.launch(headless=True)
        
        #tworzymy nową sesje w przeglądarce
        context = await browser.new_context()
        
        #lista skanów które trwają
        tasks = []

        #iterujemy przez url w liscie
        for base in TARGET_BASE:
            
            #iterujmy przez miejsca w której mogą być podatności
            for sink in SINKS:
                
                #nasz cel
                target = f"{base}{sink}"
                
                #iterujmy przez kazdy skrypt javascript
                for payload in PAYLOADS:
                    #tworzmy nowy wątek do listy
                    tasks.append(xss_scan(context, payload, target))

        #czekamy az watek sie skończy
        scan_results = await asyncio.gather(*tasks)
        
        # iterujmy przez skończone wątki
        for vulnerable, payload in scan_results:
            #jeśli skrypt się wywołał na stronie wyświetlamy jaki zadziałał
            if vulnerable:
                print(f"Cel podatany na następujący skrypt: {payload}")

        #zamykamy przęglądrke
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())