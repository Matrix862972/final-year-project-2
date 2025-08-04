@echo off
echo MySQL Root Password Reset Script
echo ================================
echo.
echo This script will help you reset your MySQL root password.
echo Please follow the instructions carefully.
echo.
pause

echo Step 1: Stopping MySQL service...
net stop MySQL80
if %errorlevel% neq 0 (
    echo Failed to stop MySQL service. Please run this script as Administrator.
    pause
    exit /b 1
)

echo Step 2: Creating temporary init file...
echo ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword123'; > "%TEMP%\mysql_reset.sql"
echo FLUSH PRIVILEGES; >> "%TEMP%\mysql_reset.sql"

echo Step 3: Starting MySQL with skip-grant-tables...
echo Please wait while MySQL starts in safe mode...
start "MySQL Reset" "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --skip-grant-tables --init-file="%TEMP%\mysql_reset.sql"

echo Waiting for MySQL to initialize...
timeout /t 10 /nobreak > nul

echo Step 4: Testing new password...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pnewpassword123 -e "SHOW DATABASES;"

if %errorlevel% eq 0 (
    echo SUCCESS! Your new MySQL root password is: newpassword123
    echo.
    echo Step 5: Stopping safe mode MySQL...
    taskkill /f /im mysqld.exe > nul 2>&1
    timeout /t 3 /nobreak > nul
    
    echo Step 6: Starting MySQL service normally...
    net start MySQL80
    
    echo.
    echo Password reset complete!
    echo Your new MySQL root password is: newpassword123
    echo.
    echo You can now update your app.py file with:
    echo app.config['MYSQL_PASSWORD'] = 'newpassword123'
) else (
    echo Failed to reset password. Please try manual reset.
    taskkill /f /im mysqld.exe > nul 2>&1
    net start MySQL80
)

echo.
del "%TEMP%\mysql_reset.sql" > nul 2>&1
echo Cleanup complete.
pause
