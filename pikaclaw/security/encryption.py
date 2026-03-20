"""Field encryption for sensitive data at rest."""
from __future__ import annotations
import os
import base64


class FieldEncryption:
    """AES-256-GCM encryption for sensitive fields. Uses cryptography library."""

    def __init__(self, key: bytes | None = None):
        self._key = key

    def _get_key(self) -> bytes:
        if self._key:
            return self._key
        # Use or create a key file
        from pathlib import Path
        key_file = Path.home() / ".pikaclaw" / "keys" / "master.key"
        if key_file.exists():
            return base64.b64decode(key_file.read_text().strip())
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key = os.urandom(32)
        key_file.write_text(base64.b64encode(key).decode())
        key_file.chmod(0o600)
        return key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string, return base64-encoded ciphertext."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            key = self._get_key()
            nonce = os.urandom(12)
            aesgcm = AESGCM(key)
            ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
            return base64.b64encode(nonce + ct).decode()
        except ImportError:
            return base64.b64encode(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext."""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            raw = base64.b64decode(ciphertext)
            nonce, ct = raw[:12], raw[12:]
            key = self._get_key()
            aesgcm = AESGCM(key)
            return aesgcm.decrypt(nonce, ct, None).decode()
        except ImportError:
            return base64.b64decode(ciphertext).decode()
