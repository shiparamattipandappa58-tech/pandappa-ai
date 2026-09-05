CREATE DATABASE college_db;
USE college_db;

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_no VARCHAR(500),
    student_name VARCHAR(1000),
    status VARCHAR(20),
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

