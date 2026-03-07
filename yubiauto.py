import binascii
import subprocess
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def get_yubikey_response(challenge_hex):
    """Zwraca odpowiedź YubiKey (hex string) dla zadanego challenge."""
    try:
        result = subprocess.run(
            ['ykman', 'otp', 'calculate', '2', challenge_hex],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Błąd ykman: {e.stderr}")
        return None
    except FileNotFoundError:
        logging.error("ykman nie znaleziony. Zainstaluj YubiKey Manager.")
        return None

def odszyfruj_haslo(challenge_hex, encrypted_password, iv, tag):
    """Pobiera response z YubiKey i odszyfrowuje hasło."""
    response_hex = get_yubikey_response(challenge_hex)
    if not response_hex:
        return None

    response_bytes = binascii.unhexlify(response_hex)
    key = response_bytes[:16]  # pierwsze 16 bajtów = klucz AES-128

    try:
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()
        plaintext = decryptor.update(encrypted_password) + decryptor.finalize()
        return plaintext.decode('utf-8')
    except Exception as e:
        logging.error(f"Błąd deszyfrowania: {e}")
        return None