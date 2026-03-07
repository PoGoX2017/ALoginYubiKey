import os
import binascii
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

CHALLENGE = "416C6F67696E"  # "Alogin" w hex – stały challenge

def get_yubikey_response(challenge_hex):
    """Wywołuje ykman i zwraca odpowiedź z YubiKey (hex)."""
    try:
        result = subprocess.run(
            ['ykman', 'otp', 'calculate', '2', challenge_hex],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Błąd ykman:", e.stderr)
        return None
    except FileNotFoundError:
        print("ykman nie jest zainstalowany lub nie w PATH.")
        return None

def encrypt_aes_gcm(key, plaintext):
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return iv, ciphertext, encryptor.tag

def main():
    print("=== Szyfrowanie hasła z YubiKey ===\n")
    response_hex = get_yubikey_response(CHALLENGE)
    if not response_hex:
        print("Nie można uzyskać odpowiedzi z YubiKey. Sprawdź, czy klucz jest wpięty i slot 2 skonfigurowany.")
        return

    response_bytes = binascii.unhexlify(response_hex)
    key = response_bytes[:16]  # AES-128 (pierwsze 16 bajtów)

    windows_password = input("Wprowadź swoje hasło do Windows: ").strip()
    iv, ciphertext, tag = encrypt_aes_gcm(key, windows_password)

    with open("config.py", "w") as f:
        f.write("# Zaszyfrowane dane logowania\n")
        f.write("# Wygenerowano przez encrypt_helper.py\n\n")
        f.write(f"CHALLENGE = {repr(CHALLENGE)}\n")
        f.write(f"ENCRYPTED_PASSWORD = {repr(ciphertext)}\n")
        f.write(f"IV = {repr(iv)}\n")
        f.write(f"TAG = {repr(tag)}\n")

    print("\nSukces! Dane zapisane w config.py")

if __name__ == "__main__":
    main()