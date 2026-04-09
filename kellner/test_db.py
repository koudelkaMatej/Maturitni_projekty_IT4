#!/usr/bin/env python3
"""
Database diagnostic script
"""
import mysql.connector
from pripojeni import *

print("=" * 60)
print("DATABASE DIAGNOSTIC TEST")
print("=" * 60)

# Test connection
print(f"\nTesting connection to: {HOST}")
print(f"User: {USER}")
print(f"Database: {DATABASE}")
print()

try:
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    print("✓ Connection successful!")
    
    cursor = conn.cursor()
    
    # Check if table exists
    print("\nChecking for Ubermosh table...")
    try:
        cursor.execute("SELECT COUNT(*) FROM Ubermosh")
        count = cursor.fetchone()[0]
        print(f"✓ Table exists with {count} records")
        
        # Describe table
        cursor.execute("DESCRIBE Ubermosh")
        columns = cursor.fetchall()
        print("\nTable schema:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # List all users
        cursor.execute("SELECT nickname, score, gamemode, status FROM Ubermosh")
        users = cursor.fetchall()
        print(f"\nAll users ({len(users)} total):")
        for user in users:
            print(f"  - {user[0]}: score={user[1]}, mode={user[2]}, status={user[3]}")
        
        # Check admin user
        cursor.execute("SELECT password FROM Ubermosh WHERE nickname = 'admin'")
        result = cursor.fetchone()
        if result:
            print(f"\n✓ 'admin' user exists with password hash: {result[0][:20]}...")
        else:
            print("\n✗ 'admin' user not found")
        
        # Check snus user
        cursor.execute("SELECT password FROM Ubermosh WHERE nickname = 'snus'")
        result = cursor.fetchone()
        if result:
            print(f"✓ 'snus' user exists with password hash: {result[0][:20]}...")
        else:
            print("✗ 'snus' user not found")
            
    except mysql.connector.Error as e:
        print(f"✗ Table error: {e}")
        print("\nAttempting to create table...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Ubermosh (
                    nickname VARCHAR(255) PRIMARY KEY,
                    score INT DEFAULT 0,
                    gamemode VARCHAR(50) DEFAULT 'Normal',
                    status VARCHAR(50) DEFAULT 'Registered',
                    password VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            print("✓ Table created successfully!")
        except mysql.connector.Error as e2:
            print(f"✗ Failed to create table: {e2}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"✗ Connection failed: {e}")
    print(f"\nPossible causes:")
    print(f"  1. Database server not accessible")
    print(f"  2. Wrong credentials (check pripojeni.py)")
    print(f"  3. Network/firewall issue")

print("\n" + "=" * 60)
