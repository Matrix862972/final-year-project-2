@echo off
echo Setting up MySQL database for Online Exam Proctor...
echo.

REM Add MySQL to PATH
set PATH=%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin

echo You will be prompted for your MySQL root password.
echo.

REM Create database
echo Creating database...
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS examproctordb;"

if %errorlevel% neq 0 (
    echo Error creating database. Please check your password and try again.
    pause
    exit /b 1
)

echo Database created successfully!
echo.

REM Create tables and insert data
echo Creating tables and inserting sample data...
mysql -u root -p examproctordb < setup_database.sql

if %errorlevel% neq 0 (
    echo Error setting up tables. Please check the setup manually.
    pause
    exit /b 1
)

echo.
echo Database setup completed successfully!
echo You can now run your Flask application.
echo.
echo Default login credentials:
echo Admin - Email: admin@example.com, Password: admin123
echo Student - Email: john.doe@example.com, Password: student123
echo.
pause
