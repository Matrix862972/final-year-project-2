# Password Hashing Migration Guide

## Overview

This guide explains how to migrate from plain text passwords to secure hashed passwords in the exam proctoring system.

## ⚠️ IMPORTANT: Read Before Proceeding

**BACKUP YOUR DATABASE FIRST!** This migration will modify all existing passwords in your database.

## Steps to Apply Password Hashing

### Step 1: Install Required Dependencies

Make sure you have the required Python packages:

```bash
pip install mysql-connector-python werkzeug
```

### Step 2: Backup Your Database

Create a backup of your `examproctordb` database before proceeding:

```bash
mysqldump -u root -p examproctordb > examproctordb_backup.sql
```

### Step 3: Run the Password Migration Script

Execute the migration script to hash existing passwords:

```bash
python migrate_passwords.py
```

The script will:

- Connect to your database
- Show you how many students will be affected
- Ask for confirmation before proceeding
- Hash all existing plain text passwords
- Verify the migration was successful

### Step 4: Test the Migration

After running the migration:

1. Try logging in with existing user credentials
2. The same passwords should work (they're now hashed in the database)
3. Create a new user to verify new registrations work

### Step 5: Deploy Updated Application

The updated `app.py` now includes:

- Password hashing for new registrations (`insertStudent`)
- Password hashing for updates (`updateStudent`)
- Secure login verification using `check_password_hash`

## What Changed

### Before (Insecure)

```python
# Plain text password storage
cur.execute("INSERT INTO students (Name, Email, Password, Role) VALUES (%s, %s, %s, %s)",
           (name, email, password, 'STUDENT'))

# Plain text password login
cur.execute("SELECT * FROM students WHERE Email=%s AND Password=%s", (username, password))
```

### After (Secure)

```python
# Hashed password storage
hashed_password = generate_password_hash(password)
cur.execute("INSERT INTO students (Name, Email, Password, Role) VALUES (%s, %s, %s, %s)",
           (name, email, hashed_password, 'STUDENT'))

# Secure password verification
cur.execute("SELECT * FROM students WHERE Email=%s", (username,))
data = cur.fetchone()
if data and check_password_hash(stored_password, password):
    # Login successful
```

## Security Benefits

1. **Database Breach Protection**: Even if the database is compromised, attackers cannot see actual passwords
2. **One-Way Hashing**: Passwords cannot be "unhashed" - only verified
3. **Salt Protection**: Each password gets a unique salt to prevent rainbow table attacks
4. **Industry Standard**: Uses PBKDF2 with SHA-256, a widely accepted secure hashing method

## Troubleshooting

### Migration Script Issues

- **Database Connection Error**: Check your database credentials in `migrate_passwords.py`
- **Permission Error**: Make sure your database user has UPDATE privileges
- **Already Hashed**: The script will skip passwords that are already hashed

### Login Issues After Migration

- **Can't Login**: Verify the migration completed successfully by running the verification
- **New Users Can't Login**: Check that `werkzeug.security` is imported in `app.py`

### Rollback (Emergency Only)

If you need to rollback:

```bash
mysql -u root -p examproctordb < examproctordb_backup.sql
```

## Files Modified

1. **`app.py`**: Updated login, insertStudent, and updateStudent functions
2. **`migrate_passwords.py`**: One-time migration script for existing passwords
3. **`PASSWORD_MIGRATION_README.md`**: This documentation

## Testing Checklist

- [ ] Database backup created
- [ ] Migration script executed successfully
- [ ] Existing users can still login with same passwords
- [ ] New user registration creates hashed passwords
- [ ] Password updates hash the new password
- [ ] Login attempts with wrong passwords are rejected

## Support

If you encounter issues:

1. Check the migration script output for errors
2. Verify database connection settings
3. Ensure all dependencies are installed
4. Check application logs for detailed error messages

---

**Security Note**: This migration addresses Bug #6 (Passwords Stored in Plain Text) from the KNOWN_BUGS.md file, elevating the security from "Critical" to "Secure".
