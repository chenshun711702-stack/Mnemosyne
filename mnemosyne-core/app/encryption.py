from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionManager:
    @staticmethod
    def derive_key(passphrase: str, salt: bytes = b'mnemosyne_salt_fixed') -> bytes:
        """Derives a Fernet-compatible key from a passphrase."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    def __init__(self, passphrase: str):
        self.key = self.derive_key(passphrase)
        self.fernet = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return "[DECRYPTION_FAILED]"
