-- Online Exam Proctor Database Setup
-- This script creates the required database and tables for the Online Exam Proctor system

-- Create the database
CREATE DATABASE IF NOT EXISTS examproctordb;
USE examproctordb;

-- Create the students table
CREATE TABLE IF NOT EXISTS students (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    Role ENUM('STUDENT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert a default admin user
INSERT INTO students (Name, Email, Password, Role) VALUES 
('Admin User', 'admin@example.com', 'admin123', 'ADMIN');

-- Insert some sample students (optional)
INSERT INTO students (Name, Email, Password, Role) VALUES 
('John Doe', 'john.doe@example.com', 'student123', 'STUDENT'),
('Jane Smith', 'jane.smith@example.com', 'student123', 'STUDENT'),
('Bob Johnson', 'bob.johnson@example.com', 'student123', 'STUDENT');

-- Display the created tables
SHOW TABLES;

-- Display the students table structure
DESCRIBE students;

-- Display all users
SELECT * FROM students;
