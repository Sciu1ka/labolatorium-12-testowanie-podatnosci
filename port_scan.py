import socket
import sys

#importujemy biblioteke która pozwala nam na wykonywanie zadań w wielu wątkach jednocześnie
from concurrent.futures import ThreadPoolExecutor, as_completed
#importujemy bibliotekę do wyświetlania postępu skanowania
import tqdm

WORKERS = 20

#funckja która skanuje pojedyńczy port
def scan_port(ip, port):
    #tworzymy gniazdo socket | AF_INET - oznacza że używamy protokołu IPv4, SOCK_STREAM - oznacza że używamy protokołu TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1) #ustawiamy timeout na 1 sekundę, aby nie czekać zbyt długo na odpowiedź
            result = s.connect_ex((ip, port)) #łączymy sie z danym IP i portem, connect_ex zwraca 0 jeśli połączenie jest udane, lub kod błędu jeśli nie
            if result == 0:
                try:
                    #próbujemy pobrać nazwę usługi działającej na danym porcie
                    service = socket.getservbyport(port, 'tcp')
                    return port, service
                except OSError:
                    return port, "Unknown"
    return None

if __name__ == "__main__":
    
    ip = input("podaj adres IP: ")
    port_range = input("podaj zakres portów do skanowania (np. 1-1000, lub 80,443): ")
    
    #obsługa różnych formatów zakresu portów
    if '-' in port_range:
        start_port, end_port = map(int, port_range.split('-'))
        ports_to_scan = range(start_port, end_port + 1)            
    elif ',' in port_range:
        ports_to_scan = map(int, port_range.split(','))
    else:
        print("Nieprawidłowy format zakresu portów. Proszę użyć 'początek-koniec' lub 'port1,port2,...'")
        exit(-1)
        
    try:
        #używamy ThreadPoolExecutor do skanowania portów w wielu wątkach jednocześnie, co przyspiesza proces skanowania
        #max_workers=20 oznacza że jednocześnie będzie skanowanych 20 portów
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            
            futures = []
            for port in ports_to_scan:
                #dodajemy zadanie skanowania portu do puli wątków
                futures.append(executor.submit(scan_port, ip, port))
            
            results = []
            #używamy tqdm do wyświetlania postępu skanowania, as_completed pozwala nam na iterowanie po wynikach w miarę ich pojawiania się
            for future in tqdm.tqdm(as_completed(futures), total=len(futures), desc="Skanowanie portów", unit="port"):
                #przypisujemy wynik skanowania do listy results
                results.append(future.result())
        
        #iterujemy po wynikach i wyświetlamy otwarte porty wraz z nazwami usług
        for result in results:
            if result is not None:
                print(f"Port {result[0]} jest otwarty (Service: {result[1]})")


    except KeyboardInterrupt:
        print("\nSkanowanie przerwane przez użytkownika.")
        sys.exit(0)