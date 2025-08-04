# MySQL Setup Guide for Online Exam Proctor

## Prerequisites

- MySQL Server installed on your system
- MySQL running on localhost (default port 3306)

## Setup Steps

### 1. Install MySQL (if not already installed)

Download and install MySQL from: https://dev.mysql.com/downloads/mysql/

### 2. Start MySQL Service

Make sure MySQL service is running:

- **Windows:** Open Services and start "MySQL80" (or your MySQL version)
- **Or via Command Prompt (as Administrator):**
  ```cmd
  net start mysql80
  ```

### 3. Create Database and Tables

You have two options:

#### Option A: Using MySQL Command Line

1. Open Command Prompt as Administrator
2. Connect to MySQL:
   ```cmd
   mysql -u root -p
   ```
3. Enter your MySQL root password (if you set one during installation)
4. Run the SQL setup script:
   ```sql
   source d:\Python\final-year-project-2\The-Online-Exam-Proctor\setup_database.sql
   ```

#### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your local MySQL instance
3. Open the `setup_database.sql` file
4. Execute the script

### 4. Update Application Configuration (if needed)

The current configuration in `app.py` is:

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Empty password
app.config['MYSQL_DB'] = 'examproctordb'
```

If your MySQL setup is different, update these values accordingly.

### 5. Test Database Connection

Run your Flask application:

```cmd
cd "d:\Python\final-year-project-2\The-Online-Exam-Proctor"
python app.py
```

### Default Login Credentials

After setup, you can use these credentials:

**Admin Login:**

- Email: admin@example.com
- Password: admin123

**Student Login:**

- Email: john.doe@example.com
- Password: student123

## Troubleshooting

### Common Issues:

1. **MySQL Service Not Running**

   - Start the MySQL service as described in step 2

2. **Access Denied Error**

   - Check if the root password is correct
   - If you set a password during MySQL installation, update `app.py`:
     ```python
     app.config['MYSQL_PASSWORD'] = 'your_password_here'
     ```

3. **Database Connection Error**

   - Verify MySQL is running on localhost:3306
   - Check firewall settings
   - Ensure the database `examproctordb` exists

4. **Permission Issues**
   - Run Command Prompt as Administrator
   - Ensure the MySQL user has proper privileges

### Verify Setup

To verify everything is working:

1. Start the Flask application
2. Navigate to `http://localhost:5000`
3. Try logging in with the admin credentials
4. Check if you can access the admin panel and student management

## Database Schema

The `students` table structure:

- `ID`: Auto-increment primary key
- `Name`: Student/Admin name
- `Email`: Unique email (used for login)
- `Password`: Plain text password (consider hashing in production)
- `Role`: Either 'STUDENT' or 'ADMIN'
- `created_at`: Timestamp of creation
