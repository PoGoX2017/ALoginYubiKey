from win32 import win32crypt
import binascii


def encrypt_data(data, description=""):
    """Szyfruje dane za pomocą DPAPI."""
    encrypted = win32crypt.CryptProtectData(
        data.encode('utf-8') if isinstance(data, str) else data,
        description,
        None,
        None,
        None,
        0
    )
    return encrypted

def decrypt_data(encrypted_data):
    return win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)[1]

if __name__ == "__main__":
    print("=== Szyfrowanie danych dla YubiKey Auto Login ===\n")

    # Krok 1: Wprowadź swój klucz tajny (ten z YubiKey Managera)
    secret_hex = input("Wprowadź swój klucz tajny (w formacie hex, 40 znaków): ").strip()
    try:
        secret_bytes = binascii.unhexlify(secret_hex)
    except:
        print("Błąd: Nieprawidłowy format hex. Upewnij się, że to 40 znaków (0-9, A-F).")
        exit(1)

    # Krok 2: Wprowadź hasło do Windows
    windows_password = input("Wprowadź swoje hasło do Windows: ").strip()

    # Krok 3: Zaszyfruj oba sekrety
    encrypted_secret = encrypt_data(secret_bytes, "YubiKey Secret")
    encrypted_password = encrypt_data(windows_password, "Windows Password")

    # Krok 4: Zapisz zaszyfrowane dane do pliku config.py
    with open("encrypted.txt", "w") as f:
        f.write("# Ten plik zawiera zaszyfrowane dane logowania\n")
        f.write("# Zostal wygenerowany przez encrypt_helper.py\n\n")
        f.write(f"ENCRYPTED_SECRET = {encrypted_secret}\n")
        f.write(f"ENCRYPTED_PASSWORD = {encrypted_password}\n")

    print("\nSukces! Zaszyfrowane dane zapisano w pliku config.py")
    print("Możesz teraz usunąć encrypt_helper.py lub zachować na przyszłość.")