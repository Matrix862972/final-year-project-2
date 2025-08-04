# PowerShell script to setup MySQL database for Online Exam Proctor
# This script will prompt for MySQL root password and create the database

$mysqlPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

Write-Host "Setting up MySQL database for Online Exam Proctor..." -ForegroundColor Green
Write-Host "You will be prompted for your MySQL root password." -ForegroundColor Yellow

# Add MySQL to PATH for this session
$env:PATH += ";C:\Program Files\MySQL\MySQL Server 8.0\bin"

# Prompt for password
$password = Read-Host "Enter MySQL root password" -AsSecureString
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# Create database
Write-Host "Creating database..." -ForegroundColor Blue
$createDB = "CREATE DATABASE IF NOT EXISTS examproctordb;"
echo $createDB | mysql -u root -p$plainPassword

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database created successfully!" -ForegroundColor Green
    
    # Create table and insert data
    Write-Host "Creating table and inserting sample data..." -ForegroundColor Blue
    
    $sqlCommands = @"
USE examproctordb;

CREATE TABLE IF NOT EXISTS students (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    Role ENUM('STUDENT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO students (Name, Email, Password, Role) VALUES 
('Admin User', 'admin@example.com', 'admin123', 'ADMIN');

INSERT INTO students (Name, Email, Password, Role) VALUES 
('John Doe', 'john.doe@example.com', 'student123', 'STUDENT'),
('Jane Smith', 'jane.smith@example.com', 'student123', 'STUDENT'),
('Bob Johnson', 'bob.johnson@example.com', 'student123', 'STUDENT');
"@

    echo $sqlCommands | mysql -u root -p$plainPassword
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database setup completed successfully!" -ForegroundColor Green
        Write-Host "You can now run your Flask application." -ForegroundColor Green
        Write-Host ""
        Write-Host "Default login credentials:" -ForegroundColor Cyan
        Write-Host "Admin - Email: admin@example.com, Password: admin123" -ForegroundColor White
        Write-Host "Student - Email: john.doe@example.com, Password: student123" -ForegroundColor White
    } else {
        Write-Host "Error creating tables. Please check the setup_database.sql file manually." -ForegroundColor Red
    }
} else {
    Write-Host "Error creating database. Please check your password and try again." -ForegroundColor Red
}

# Clear password from memory
$plainPassword = $null
[System.GC]::Collect()
