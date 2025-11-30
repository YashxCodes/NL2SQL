CREATE DATABASE IF NOT EXISTS company_db;
USE company_db;


DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;


CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(50)
);


CREATE TABLE employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    dept VARCHAR(50),
    salary DECIMAL(10,2)
);


CREATE TABLE projects (
    proj_id INT PRIMARY KEY AUTO_INCREMENT,
    proj_name VARCHAR(100),
    emp_id INT,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);


INSERT INTO departments (dept_name) VALUES
('HR'),
('Engineering'),
('Marketing');

INSERT INTO employees (name, dept, salary) VALUES
('Alice', 'HR', 50000.00),
('Bob', 'Engineering', 70000.00),
('Carol', 'Marketing', 60000.00);

INSERT INTO projects (proj_name, emp_id) VALUES
('Apollo', 2),
('Zenith', 1),
('Nova', 3);