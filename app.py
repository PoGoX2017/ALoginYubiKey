import threading
import logging
import pystray
from PIL import Image, ImageDraw
from yubiauto import znajdz_yubikey, uwierzytelnij

logging.basicConfig(level=logging.INFO)

def utworz_ikone():
    """Tworzy prostą ikonę (możesz wczytać plik)."""
    # Przykład: rysujemy żółty kwadrat na czarnym tle
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill='green')
    return image

def autoryzuj(icon, item):
    """Wywoływane po kliknięciu menu."""
    # Uruchamiamy w osobnym wątku, by nie blokować tray'a
    threading.Thread(target=wykonaj_autoryzacje, daemon=True).start()

def wykonaj_autoryzacje():
    logging.info("Szukam YubiKey...")
    device = znajdz_yubikey()
    if not device:
        logging.error("Nie znaleziono YubiKey")
        # Możesz wyświetlić powiadomienie systemowe (np. przez pystray)
        return
    try:
        logging.info("Proszę dotknij YubiKey...")
        assertion = uwierzytelnij(device)
        logging.info("Autoryzacja udana: %s", assertion)
        # Tutaj możesz odblokować funkcje aplikacji, np. wyświetlić okno
    except Exception as e:
        logging.error("Błąd autoryzacji: %s", e)

def zakoncz(icon, item):
    icon.stop()

# Budowa menu
menu = pystray.Menu(
    pystray.MenuItem("Autoryzuj YubiKey", autoryzuj),
    pystray.MenuItem("Wyjście", zakoncz)
)

# Tworzenie ikony
ikona = pystray.Icon("yubiapp", utworz_ikone(), "YubiKey App", menu)

if __name__ == "__main__":
    ikona.run()