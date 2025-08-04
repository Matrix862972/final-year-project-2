# Alternative Methods to Handle MySQL Password

## Method 1: Check Saved Passwords in MySQL Workbench

1. Open MySQL Workbench
2. Look for saved connections - the password might be stored there
3. Try connecting with existing connections

## Method 2: Reset Password Using MySQL Workbench

1. Open MySQL Workbench
2. Go to "Server" menu → "Users and Privileges"
3. If you can connect as root, change the password there

## Method 3: Manual Password Reset (Advanced)

1. Stop MySQL service:

   ```cmd
   net stop MySQL80
   ```

2. Create init file with this content:

   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword123';
   FLUSH PRIVILEGES;
   ```

3. Start MySQL with init file:

   ```cmd
   "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --init-file=C:\path\to\init-file.sql
   ```

4. Stop and restart MySQL normally

## Method 4: Use Empty Password (Not Recommended)

If you want to remove the password entirely:

1. Reset password to empty string
2. Keep app.py as: `app.config['MYSQL_PASSWORD'] = ''`

## Method 5: Create New MySQL User (Recommended)

Instead of using root, create a new user for your application:

```sql
CREATE USER 'examuser'@'localhost' IDENTIFIED BY 'exam123';
GRANT ALL PRIVILEGES ON examproctordb.* TO 'examuser'@'localhost';
FLUSH PRIVILEGES;
```

Then update app.py:

```python
app.config['MYSQL_USER'] = 'examuser'
app.config['MYSQL_PASSWORD'] = 'exam123'
```
