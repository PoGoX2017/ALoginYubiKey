import os
import logging
from fido2.hid import CtapHidDevice
from fido2.client import Fido2Client
from fido2.webauthn import PublicKeyCredentialRequestOptions
from fido2.server import Fido2Server

# Dla celów demonstracyjnych używamy stałego origin i rp_id.
# W rzeczywistej aplikacji możesz je dostosować.
RP_ID = "ALYK.local"
ORIGIN = f"https://{RP_ID}"

def znajdz_yubikey():
    """Zwraca pierwszy znaleziony YubiKey lub None."""
    devices = list(CtapHidDevice.list_devices())
    if devices:
        return devices[0]
    return None

def uwierzytelnij(device, challenge=None):
    """
    Wykonuje uwierzytelnienie FIDO2.
    Zwraca assertion lub rzuca wyjątkiem.
    """
    if challenge is None:
        challenge = os.urandom(32)

    client = Fido2Client(device, ORIGIN)
    # Przygotuj żądanie (dla uproszczenia bez sprawdzania użytkownika)
    options = PublicKeyCredentialRequestOptions(
        challenge=challenge,
        rp_id=RP_ID,
    )
    # Wywołaj interakcję z kluczem (użytkownik może musieć go dotknąć)
    assertions = client.get_assertion(options)
    # Zwykle klucz zwraca jedną asercję, bierzemy pierwszą
    return assertions[0]