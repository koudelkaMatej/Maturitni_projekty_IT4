#!/usr/bin/env python3
"""
Database migration script - adds password column and initializes passwords
"""
import mysql.connector
import hashlib
from pripojeni import *

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

print("=" * 60)
print("DATABASE MIGRATION - Add password column")
print("=" * 60)

try:
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    print(f"\n✓ Connected to database")
    
    cursor = conn.cursor()
    
    # Check if password column exists
    print("\nChecking if password column exists...")
    cursor.execute("DESCRIBE Ubermosh")
    columns = [col[0] for col in cursor.fetchall()]
    
    if 'password' in columns:
        print("✓ Password column already exists")
    else:
        print("✗ Password column missing - adding it...")
        cursor.execute("""
            ALTER TABLE Ubermosh 
            ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT ''
        """)
        conn.commit()
        print("✓ Password column added")
    
    # Get all users without passwords (or with empty passwords)
    cursor.execute("SELECT nickname FROM Ubermosh WHERE password IS NULL OR password = ''")
    users_needing_password = cursor.fetchall()
    
    if users_needing_password:
        print(f"\nInitializing passwords for {len(users_needing_password)} users...")
        admin_hash = hash_password('admin')
        
        for user in users_needing_password:
            nickname = user[0]
            cursor.execute(
                "UPDATE Ubermosh SET password = %s WHERE nickname = %s",
                (admin_hash, nickname)
            )
            print(f"  ✓ Set password for '{nickname}' to 'admin' (hashed)")
        
        conn.commit()
        print(f"\n✓ All users now have password 'admin' as default")
    else:
        print("\n✓ All users already have passwords")
    
    # Verify
    print("\n\nVerifying table:")
    cursor.execute("SELECT nickname, score, status FROM Ubermosh ORDER BY nickname")
    users = cursor.fetchall()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"  - {user[0]}: score={user[1]}, status={user[2]}")
    
    cursor.close()
    conn.close()
    print("\n✓ Migration complete!")
    
except mysql.connector.Error as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
