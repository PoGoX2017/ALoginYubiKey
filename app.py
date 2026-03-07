import threading
import logging
import time
import ctypes
import subprocess

import pystray
from PIL import Image, ImageDraw
import pyautogui

from yubiauto import odszyfruj_haslo
from config import CHALLENGE, ENCRYPTED_PASSWORD, IV, TAG

logging.basicConfig(level=logging.INFO)

# Stan YubiKey9854

yubikey_obecny = False
pyautogui.FAILSAFE = False
def utworz_ikone():
    """Prosta ikona – zielony kwadrat."""
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill='green')
    return image

def czy_yubikey_podlaczony():
    """Sprawdza przez ykman, czy YubiKey jest podłączony."""
    try:
        result = subprocess.run(['ykman', 'list'], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False

def zablokuj_komputer():
    """Blokuje stację roboczą."""
    ctypes.windll.user32.LockWorkStation()
    logging.info("Komputer zablokowany")

def wykonaj_autoryzacje():
    """Pobiera hasło z YubiKey i wpisuje je."""
    logging.info("Próba autoryzacji...")
    haslo = odszyfruj_haslo(CHALLENGE, ENCRYPTED_PASSWORD, IV, TAG)
    if haslo:
        logging.info("Hasło odszyfrowane, wpisywanie...")
        pyautogui.typewrite(haslo)
        pyautogui.press('enter')
    else:
        logging.error("Nie udało się odszyfrować hasła")

def autoryzuj_recznie(icon, item):
    """Ręczne wywołanie autoryzacji z menu."""
    threading.Thread(target=wykonaj_autoryzacje, daemon=True).start()

def zakoncz(icon, item):
    icon.stop()

def monitoruj():
    """Wątek monitorujący zmiany stanu YubiKey."""
    global yubikey_obecny
    while True:
        time.sleep(1)
        obecny = czy_yubikey_podlaczony()
        if obecny and not yubikey_obecny:
            logging.info("YubiKey włożony")
            threading.Thread(target=wykonaj_autoryzacje, daemon=True).start()
        elif not obecny and yubikey_obecny:
            logging.info("YubiKey wyjęty – blokada")
            zablokuj_komputer()
        yubikey_obecny = obecny

# Menu tray
menu = pystray.Menu(
    pystray.MenuItem("Autoryzuj YubiKey", autoryzuj_recznie),
    pystray.MenuItem("Wyjście", zakoncz)
)

ikona = pystray.Icon("yubiapp", utworz_ikone(), "YubiKey Auto Login", menu)

if __name__ == "__main__":
    # Inicjalizacja stanu
    yubikey_obecny = czy_yubikey_podlaczony()
    # Uruchom wątek monitorujący
    threading.Thread(target=monitoruj, daemon=True).start()
    ikona.run()