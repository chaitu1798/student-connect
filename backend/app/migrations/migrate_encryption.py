import sqlite3
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import settings
from app.utils.crypto import encrypt_aes_gcm, decrypt_aes_gcm

def migrate_database():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, skipping migration.")
        return 0

    print(f"Opening database for encryption migration: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, pan_number, aadhaar_number FROM student_private_data")
    rows = cursor.fetchall()
    migrated_count = 0

    for row_id, pan, aadhaar in rows:
        needs_update = False
        new_pan = pan
        new_aadhaar = aadhaar

        if pan and not str(pan).startswith("gcm1:"):
            new_pan = encrypt_aes_gcm(pan)
            needs_update = True

        if aadhaar and not str(aadhaar).startswith("gcm1:"):
            new_aadhaar = encrypt_aes_gcm(aadhaar)
            needs_update = True

        if needs_update:
            cursor.execute(
                "UPDATE student_private_data SET pan_number = ?, aadhaar_number = ? WHERE id = ?",
                (new_pan, new_aadhaar, row_id)
            )
            migrated_count += 1

    conn.commit()
    conn.close()
    print(f"Migration complete: {migrated_count} records encrypted with AES-256-GCM.")
    return migrated_count

if __name__ == "__main__":
    migrate_database()
