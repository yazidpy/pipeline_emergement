import sys
import os
from pathlib import Path

# Roots
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils.db import connect_postgres
from utils.auth import hash_password

def create_user(login, password, role="admin"):
    conn = connect_postgres()
    try:
        with conn.cursor() as cur:
            hashed = hash_password(password)
            cur.execute("""
                INSERT INTO ref.credentials (login, password_hash, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (login) DO UPDATE SET password_hash = EXCLUDED.password_hash
            """, (login, hashed, role))
            conn.commit()
            print(f"✅ Compte '{login}' créé avec succès (Rôle: {role}).")
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Paramètres personnalisables
    create_user("yazid", "Golden2024!", "admin")
