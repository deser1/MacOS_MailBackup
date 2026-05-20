# macOS Mail Backup to NAS (QNAP)

Proste narzędzie z interfejsem graficznym (GUI) napisane w Pythonie, służące do wykonywania kopii zapasowych wiadomości e-mail. Aplikacja łączy się ze skrzynką pocztową za pomocą protokołu IMAP, filtruje wiadomości po wskazanej domenie nadawcy i zapisuje je w uniwersalnym formacie `.eml` bezpośrednio w wybranym folderze – idealnie sprawdzając się przy archiwizacji na dyski sieciowe (np. QNAP, Synology) z poziomu systemu macOS.

## 🌟 Główne funkcje

- **Dwa tryby pracy:** Wybór pomiędzy bezpiecznym pobieraniem przez IMAP, a eksperymentalnym skanowaniem lokalnych plików Apple Mail na dysku.
- **Prosty interfejs użytkownika:** Stworzony z użyciem wbudowanej w Pythona biblioteki `tkinter`.
- **Wsparcie dla IMAP:** Bezpieczne połączenie z dowolnym dostawcą poczty (Gmail, Outlook, iCloud, własne serwery).
- **Filtrowanie po domenie:** Możliwość pobrania tylko tych e-maili, które pochodzą od nadawców z konkretnej domeny (np. `@twojafirma.pl`).
- **Uniwersalny format zapisu:** Zapisywanie wiadomości jako pliki `.eml`, które można później otworzyć w większości klientów pocztowych (Apple Mail, Thunderbird, Outlook).
- **Przyjazny dla macOS i NAS:** Skrypt ułatwia wybór folderów sieciowych, domyślnie kierując użytkownika do katalogu `/Volumes/`, gdzie macOS montuje dyski SMB.

## 🚀 Wymagania

Skrypt opiera się na standardowych bibliotekach Pythona, co oznacza, że w większości przypadków nie wymaga instalacji żadnych zewnętrznych pakietów.

- **Python 3.x**
- Standardowe biblioteki (wbudowane): `tkinter`, `imaplib`, `email`, `os`, `threading`

## ⚙️ Jak uruchomić?

1. Sklonuj to repozytorium lub pobierz plik `mac_mail_backup.py`.
2. Otwórz terminal w katalogu z plikiem.
3. Uruchom skrypt poleceniem:
   ```bash
   python3 mac_mail_backup.py
   ```

## 🖥 Jak połączyć się z QNAP na macOS?

Aplikacja wymaga wskazania lokalnego lub zmapowanego folderu docelowego. Aby zapisać maile bezpośrednio na serwerze QNAP z systemu macOS:
1. Otwórz aplikację **Finder**.
2. Na górnym pasku wybierz **Idź (Go)** -> **Połącz z serwerem... (Connect to Server...)** (lub użyj skrótu `Cmd + K`).
3. Wpisz adres swojego serwera QNAP, np. `smb://192.168.1.100` i kliknij **Połącz**.
4. W aplikacji `Mail Backup`, klikając **Przeglądaj...**, wybierz swój zamontowany dysk sieciowy (będzie znajdował się w ukrytym, ale dostępnym z poziomu aplikacji folderze `/Volumes/`).

## 🔐 Uwaga dotycząca logowania (Hasła Aplikacji)

Jeśli korzystasz z dostawców takich jak **Google (Gmail)**, **Apple (iCloud)** lub **Microsoft (Office 365)**, standardowe hasło do konta może nie zadziałać ze względu na Weryfikację Dwuetapową (2FA). 
Aby skrypt mógł się zalogować, musisz wygenerować **Hasło aplikacji (App Password)** w ustawieniach bezpieczeństwa swojego dostawcy poczty i to jego użyć w programie.

## 📄 Licencja
Projekt dostępny na licencji MIT - możesz go dowolnie modyfikować i używać do własnych potrzeb.
