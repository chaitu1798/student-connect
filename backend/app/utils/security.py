import os
import hashlib
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from app.config import settings

# Supported roles exactly as specified
ROLES = ["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT", "PUBLIC"]

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire_minutes = expires_delta_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc).timestamp() + (expire_minutes * 60)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc).timestamp()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token() -> str:
    return str(uuid.uuid4()) + "-" + hashlib.sha256(os.urandom(32)).hexdigest()

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None

def verify_file_signature(file_bytes: bytes, filename: str) -> bool:
    """Verifies file headers/magic bytes for safety and malware prevention."""
    if not file_bytes:
        return False
    fn = filename.lower()
    # Check max file size (25MB)
    if len(file_bytes) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        return False

    # Reject dangerous executable formats immediately
    if file_bytes.startswith(b'MZ') or file_bytes.startswith(b'\x7fELF') or file_bytes.startswith(b'<?php') or file_bytes.startswith(b'#!'):
        return False

    # Check magic signatures
    if fn.endswith('.pdf'):
        return file_bytes.startswith(b'%PDF-')
    elif fn.endswith('.xlsx'):
        return file_bytes.startswith(b'PK\x03\x04')  # ZIP format for OOXML
    elif fn.endswith('.xls'):
        return file_bytes.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1')  # OLE format
    elif fn.endswith('.csv'):
        # Disallow binary NUL bytes
        if b'\x00' in file_bytes[:1024]:
            return False
        try:
            file_bytes[:1024].decode('utf-8')
            return True
        except UnicodeDecodeError:
            try:
                file_bytes[:1024].decode('latin-1')
                return True
            except Exception:
                return False
    elif fn.endswith('.png'):
        return file_bytes.startswith(b'\x89PNG\r\n\x1a\n')
    elif fn.endswith(('.jpg', '.jpeg')):
        return file_bytes.startswith(b'\xff\xd8\xff')
    elif fn.endswith('.webp'):
        return file_bytes.startswith(b'RIFF') and b'WEBP' in file_bytes[:16]

    # Strictly reject unknown extensions
    return False

def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def mask_aadhaar(aadhaar: str | None) -> str | None:
    if not aadhaar:
        return None
    clean = str(aadhaar).strip().replace("-", "").replace(" ", "")
    if len(clean) >= 4:
        return "XXXX-XXXX-" + clean[-4:]
    return "XXXX"

def mask_pan(pan: str | None) -> str | None:
    if not pan:
        return None
    clean = str(pan).strip().upper()
    if len(clean) >= 4:
        return clean[:2] + "XXXXX" + clean[-3:]
    return "XXXXX"

def calculate_duration_weeks(start_date, end_date) -> int | None:
    """Inclusive date convention: (end_date - start_date).days + 1"""
    if not start_date or not end_date:
        return None
    days = (end_date - start_date).days + 1
    if days <= 0:
        return 0
    return max(1, round(days / 7))
