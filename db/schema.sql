CREATE DATABASE company_db;
USE company_db;

CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(50)
);

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name VARCHAR(50),
    dept_id INT,
    salary INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

CREATE TABLE projects (
    proj_id INT PRIMARY KEY,
    proj_name VARCHAR(50),
    emp_id INT,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

INSERT INTO departments VALUES
(1, 'HR'), (2, 'Sales'), (3, 'Engineering');

INSERT INTO employees VALUES
(101, 'Alice', 1, 55000),
(102, 'Bob', 2, 60000),
(103, 'Charlie', 3, 70000),
(104, 'David', 3, 72000);

INSERT INTO projects VALUES
(201, 'Apollo', 103),
(202, 'Zeus', 104),
(203, 'Mercury', 102);
