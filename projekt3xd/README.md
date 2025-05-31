# System Rekomendacji Szlaków Turystycznych

## Opis
System rekomendacji szlaków turystycznych to zaawansowane narzędzie, które pomaga użytkownikom znaleźć idealne trasy na podstawie ich preferencji, warunków pogodowych i innych kryteriów.

## Wymagania systemowe
- Python 3.8 lub nowszy
- pip (menedżer pakietów Pythona)
- Dostęp do internetu (do pobierania danych pogodowych)

## Instalacja

1. Sklonuj repozytorium lub pobierz pliki:
```powershell
git clone <adres-repozytorium>
# lub rozpakuj pobrane archiwum
```

2. Przejdź do katalogu projektu:
```powershell
cd projekt3xd
```

3. (Zalecane) Utwórz i aktywuj wirtualne środowisko:
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

4. Zainstaluj wymagane zależności:
```powershell
pip install -r requirements.txt
```

## Pierwsze uruchomienie

1. Upewnij się, że masz aktualne dane pogodowe:
```powershell
python update_data.py
```

2. Uruchom program główny:
```powershell
python main.py
```

## Struktura projektu
- `main.py` - główny plik programu
- `utils/` - narzędzia pomocnicze
- `data_handlers/` - obsługa danych
- `recommendation/` - silnik rekomendacji
- `api/` - integracja z API pogodowym
- `DOCUMENTATION.md` - szczegółowa dokumentacja

## Użytkowanie

1. Po uruchomieniu programu wybierz miasto lub naciśnij ENTER, aby wybrać wszystkie miasta.

2. Wybierz typ danych pogodowych:
   - 1: Dane historyczne (przeszłość)
   - 2: Prognoza pogody (teraźniejszość i przyszłość)

3. Podaj datę w formacie RRRR-MM-DD lub naciśnij ENTER dla dzisiejszej daty.

4. Wybierz kategorię trasy:
   - 1: Rodzinna (łatwe, krótkie trasy)
   - 2: Widokowa (trasy z punktami widokowymi)
   - 3: Sportowa (średnio trudne trasy)
   - 4: Ekstremalna (trudne, długie trasy)

5. Wprowadź dodatkowe kryteria (opcjonalne):
   - Poziom trudności (1-3)
   - Typ terenu (górski, nizinny, leśny, miejski)
   - Długość trasy (km)
   - Preferencje pogodowe

## Wyniki
Program wygeneruje rekomendacje w trzech formatach:
- Plik tekstowy (.txt)
- Plik JSON (.json)
- Plik CSV (.csv)

## Rozwiązywanie problemów

1. Jeśli pojawia się błąd związany z modułami:
```powershell
pip install -r requirements.txt --upgrade
```

2. Jeśli dane pogodowe są nieaktualne:
```powershell
python manage_cache.py clear
python update_data.py
```

3. Jeśli program nie znajduje tras:
   - Sprawdź połączenie z internetem
   - Upewnij się, że pliki z danymi są obecne w katalogu `api/`
   - Spróbuj ponownie z mniej restrykcyjnymi kryteriami

## Wsparcie
W razie problemów sprawdź:
- Dokumentację techniczną w pliku `DOCUMENTATION.md`
- Logi błędów w konsoli
- Upewnij się, że wszystkie zależności są zainstalowane prawidłowo














Bazując na zawartości pliku requirements.txt oraz strukturze projektu, stworzę kompletną instrukcję instalacji i uruchomienia programu na nowym komputerze.

1. Najpierw upewnij się, że masz zainstalowanego Pythona (wersja 3.8 lub nowsza). Możesz to sprawdzić komendą:
````powershell
python --version
````

2. Pobierz projekt na swój komputer:
- Sklonuj repozytorium (jeśli używasz gita) lub 
- Pobierz i rozpakuj pliki do wybranego folderu

3. Otwórz terminal (PowerShell lub Command Prompt) i przejdź do katalogu projektu:
````powershell
cd ścieżka\do\projekt3xd
````

4. (Zalecane) Utwórz i aktywuj wirtualne środowisko:
````powershell
python -m venv venv
.\venv\Scripts\Activate
````

5. Zainstaluj wymagane biblioteki z pliku requirements.txt:
````powershell
pip install -r requirements.txt
````

Wymagane biblioteki to:
- pandas==2.1.0 (do obsługi danych)
- requests==2.31.0 (do komunikacji z API)
- numpy==1.24.3 (do obliczeń)
- python-dotenv==1.0.0 (do zmiennych środowiskowych)
- aiohttp==3.8.5 (do asynchronicznych zapytań API)
- urllib3==2.0.4 (wymagane przez requests)

6. Upewnij się, że wszystkie wymagane pliki danych są obecne w strukturze projektu:
- Katalog api z plikiem `weather_dataa.json`
- Katalog data z danymi o trasach
- Plik config.py z konfiguracją

7. Uruchom program główny:
````powershell
python main.py
````

W przypadku problemów:
1. Jeśli pojawią się błędy z modułami:
````powershell
pip install -r requirements.txt --upgrade
````

2. Jeśli dane pogodowe są nieaktualne:
````powershell
python update_data.py
````

Struktura projektu powinna wyglądać tak:
```
projekt3xd/
├── main.py
├── requirements.txt
├── README.md
├── DOCUMENTATION.md
├── api/
│   └── weather_dataa.json
├── data_handlers/
├── utils/
└── recommendation/
```

Wszystkie te informacje można też znaleźć w plikach:
- README.md - podstawowe instrukcje instalacji
- DOCUMENTATION.md - szczegółowa dokumentacja
- requirements.txt - lista wymaganych bibliotek