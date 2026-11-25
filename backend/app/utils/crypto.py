import os
import hashlib
from typing import Optional
from sqlalchemy import TypeDecorator, String
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from app.config import settings

class EncryptionError(Exception):
    """Base exception for cryptographic errors."""
    pass

class DecryptionError(EncryptionError):
    """Raised when ciphertext authentication or decryption fails (wrong key, corrupted/tampered data)."""
    pass

class KeyConfigurationError(EncryptionError):
    """Raised when required cryptographic keys are missing or invalid."""
    pass

def get_encryption_key() -> bytes:
    """
    Derives an exact 256-bit (32-byte) binary key from settings.DATA_ENCRYPTION_KEY.
    If the key is 64 hex characters, parses directly; otherwise derives via SHA-256.
    Fails explicitly if required key is missing or invalid.
    """
    raw_key = settings.DATA_ENCRYPTION_KEY or ""
    if not raw_key:
        if settings.ENVIRONMENT == "production":
            raise KeyConfigurationError(
                "CRITICAL SECURITY CONFIGURATION ERROR: "
                "DATA_ENCRYPTION_KEY is required in production."
            )
        # Development / Testing fallback: Load from persistent local dev key file
        dev_key_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".dev_encryption_key")
        if os.path.exists(dev_key_file):
            try:
                with open(dev_key_file, "r", encoding="utf-8") as f:
                    raw_key = f.read().strip()
            except Exception:
                pass
        if not raw_key:
            raise KeyConfigurationError("Missing DATA_ENCRYPTION_KEY: no encryption key configured.")

    if len(raw_key) == 64:
        try:
            return bytes.fromhex(raw_key)
        except ValueError:
            pass
    return hashlib.sha256(raw_key.encode("utf-8")).digest()

def encrypt_aes_gcm(plaintext: Optional[str]) -> Optional[str]:
    """
    Encrypts plaintext string using AES-256-GCM authenticated encryption.
    Format: gcm1:<12-byte-hex-nonce>:<ciphertext-and-tag-hex>
    Prevents double-encryption if value already starts with gcm1:.
    """
    if plaintext is None:
        return None
    val_str = str(plaintext).strip()
    if not val_str:
        return None
    # Prevent accidental double-encryption
    if val_str.startswith("gcm1:"):
        return val_str

    key = get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit unique standard GCM nonce
    ciphertext = aesgcm.encrypt(nonce, val_str.encode("utf-8"), None)
    return f"gcm1:{nonce.hex()}:{ciphertext.hex()}"

def decrypt_aes_gcm(ciphertext: Optional[str]) -> Optional[str]:
    """
    Decrypts AES-256-GCM formatted ciphertext.
    Safely handles legacy plaintext records if string does not start with gcm1:.
    Raises explicit DecryptionError if authentication tag fails, key is wrong,
    or ciphertext is corrupted/tampered. Never silently converts to None!
    """
    if ciphertext is None:
        return None
    val_str = str(ciphertext).strip()
    if not val_str:
        return None
    # Graceful handling for legacy unencrypted records
    if not val_str.startswith("gcm1:"):
        return val_str

    parts = val_str.split(":")
    if len(parts) != 3 or parts[0] != "gcm1":
        raise DecryptionError("Malformed ciphertext structure: expected gcm1:<nonce>:<ciphertext>")

    try:
        _, nonce_hex, ct_hex = parts
        nonce = bytes.fromhex(nonce_hex)
        ct_bytes = bytes.fromhex(ct_hex)
    except ValueError as e:
        raise DecryptionError(f"Malformed ciphertext encoding: invalid hex data ({str(e)})")

    if len(nonce) != 12:
        raise DecryptionError(f"Invalid GCM nonce length: expected 12 bytes, got {len(nonce)}")

    key = get_encryption_key()
    aesgcm = AESGCM(key)

    try:
        decrypted_bytes = aesgcm.decrypt(nonce, ct_bytes, None)
        return decrypted_bytes.decode("utf-8")
    except InvalidTag:
        raise DecryptionError("Decryption failed: cryptographic authentication failure or invalid key")
    except UnicodeDecodeError:
        raise DecryptionError("Decryption failed: decrypted payload is not valid UTF-8 string")
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {str(e)}")

class EncryptedField(TypeDecorator):
    """
    SQLAlchemy TypeDecorator that transparently encrypts values with AES-256-GCM
    on database write (bind param) and decrypts on database read (result value).
    Guarantees:
    - Failed decryptions raise DecryptionError, preventing silent overwrite with None.
    - Preserves existing ciphertext if already encrypted.
    - Never silently downgrades to plaintext on write.
    """
    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        val_str = str(value).strip()
        if not val_str:
            return None
        # If value is already valid ciphertext, preserve it intact without re-encrypting
        if val_str.startswith("gcm1:"):
            return val_str
        return encrypt_aes_gcm(val_str)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return decrypt_aes_gcm(str(value))

# Convenience aliases
encrypt_data = encrypt_aes_gcm
decrypt_data = decrypt_aes_gcm
