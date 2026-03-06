import winreg
import sys

def dodaj_do_autostartu():
    """Dodaje bieżący program do autostartu w rejestrze."""
    klucz = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
    )
    sciezka = sys.executable  # ścieżka do interpretera (lub exe po spakowaniu)
    winreg.SetValueEx(klucz, "YubiKeyApp", 0, winreg.REG_SZ, sciezka)
    winreg.CloseKey(klucz)

def usun_z_autostartu():
    """Usuwa wpis z autostartu."""
    klucz = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
    )
    try:
        winreg.DeleteValue(klucz, "YubiKeyApp")
    except FileNotFoundError:
        pass
    winreg.CloseKey(klucz)