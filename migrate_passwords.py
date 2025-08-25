#!/usr/bin/env python3
"""
Password Migration Script
=========================

This script hashes all existing plain text passwords in the database.
Run this ONCE before deploying the updated application with password hashing.

WARNING: This will modify all passwords in the database. Make sure to backup your database first!
"""

import mysql.connector
from werkzeug.security import generate_password_hash
import getpass

def connect_to_database():
    """Connect to the MySQL database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',  # Update this to match your database password
            database='examproctordb'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def migrate_passwords():
    """Hash all existing plain text passwords"""
    connection = connect_to_database()
    
    if not connection:
        print("Failed to connect to database. Exiting.")
        return
    
    cursor = connection.cursor()
    
    try:
        # First, let's see how many students we have
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        print(f"Found {total_students} students in the database.")
        
        if total_students == 0:
            print("No students found. Nothing to migrate.")
            return
        
        # Ask for confirmation
        print("\n⚠️  WARNING: This will hash all existing passwords!")
        print("⚠️  Make sure you have backed up your database!")
        confirm = input("\nDo you want to proceed? (type 'YES' to continue): ")
        
        if confirm != 'YES':
            print("Migration cancelled.")
            return
        
        # Fetch all students with their current passwords
        cursor.execute("SELECT ID, Name, Email, Password FROM students")
        students = cursor.fetchall()
        
        migrated_count = 0
        
        print("\nStarting password migration...")
        
        for student_id, name, email, current_password in students:
            # Check if password is already hashed (starts with pbkdf2:sha256)
            if current_password.startswith('pbkdf2:sha256'):
                print(f"Skipping {email} - already hashed")
                continue
            
            # Hash the current password
            hashed_password = generate_password_hash(current_password)
            
            # Update the database
            update_query = "UPDATE students SET Password = %s WHERE ID = %s"
            cursor.execute(update_query, (hashed_password, student_id))
            
            migrated_count += 1
            print(f"✅ Migrated password for: {email}")
        
        # Commit all changes
        connection.commit()
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"📊 Total students: {total_students}")
        print(f"📊 Passwords migrated: {migrated_count}")
        print(f"📊 Already hashed: {total_students - migrated_count}")
        
        print("\n📝 Next steps:")
        print("1. Deploy the updated application code with password hashing")
        print("2. All users will continue to use their existing passwords")
        print("3. New registrations will automatically use hashed passwords")
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        connection.rollback()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def verify_migration():
    """Verify that the migration was successful"""
    connection = connect_to_database()
    
    if not connection:
        print("Failed to connect to database for verification.")
        return
    
    cursor = connection.cursor()
    
    try:
        # Check for any remaining plain text passwords
        cursor.execute("SELECT ID, Email, Password FROM students WHERE Password NOT LIKE 'pbkdf2:sha256%'")
        plain_text_passwords = cursor.fetchall()
        
        if plain_text_passwords:
            print(f"\n⚠️  Found {len(plain_text_passwords)} students with non-hashed passwords:")
            for student_id, email, password in plain_text_passwords:
                # Don't print the actual password for security
                print(f"   - {email} (ID: {student_id})")
        else:
            print("\n✅ All passwords are properly hashed!")
            
    except mysql.connector.Error as err:
        print(f"❌ Verification error: {err}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🔐 Password Migration Script")
    print("=" * 50)
    
    print("\nThis script will:")
    print("1. Connect to your exam proctor database")
    print("2. Hash all existing plain text passwords")
    print("3. Update the database with hashed passwords")
    
    migrate_passwords()
    
    print("\n" + "=" * 50)
    print("🔍 Verifying migration...")
    verify_migration()
    
    print("\n" + "=" * 50)
    print("Migration script completed!")
