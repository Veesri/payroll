-- Staff Payroll Management System Relational Schema Reference
-- Target Database: MySQL / MariaDB (payroll_db)

CREATE DATABASE IF NOT EXISTS payroll_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payroll_db;

-- 1. Accounts: User and Roles
CREATE TABLE IF NOT EXISTS accounts_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Employee', -- 'SuperAdmin', 'HRAdmin', 'PayrollOfficer', 'DeptManager', 'Employee'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until DATETIME NULL,
    last_ip VARCHAR(45) NULL,
    date_joined DATETIME NOT NULL,
    last_login DATETIME NULL
);

-- 2. Employees: Department, Designation, and Employee Profile
CREATE TABLE IF NOT EXISTS employees_department (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    manager_user_id INT NULL,
    FOREIGN KEY (manager_user_id) REFERENCES accounts_user(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS employees_designation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS employees_employee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    department_id INT NULL,
    designation_id INT NULL,
    date_of_joining DATE NOT NULL,
    basic_salary DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    hra DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    da DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    travel_allowance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    medical_allowance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    phone_number VARCHAR(15) NULL,
    pan_number VARCHAR(10) NULL,
    pf_account_number VARCHAR(22) NULL,
    esi_number VARCHAR(17) NULL,
    bank_account_number VARCHAR(20) NULL,
    bank_ifsc_code VARCHAR(11) NULL,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES employees_department(id) ON DELETE SET NULL,
    FOREIGN KEY (designation_id) REFERENCES employees_designation(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS employees_employeedocument (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    document_name VARCHAR(100) NOT NULL,
    document_file VARCHAR(100) NOT NULL, -- Path to file
    uploaded_at DATETIME NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees_employee(id) ON DELETE CASCADE
);

-- 3. Attendance: Check-in, out logs and correction requests
CREATE TABLE IF NOT EXISTS attendance_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    check_in DATETIME NOT NULL,
    check_out DATETIME NULL,
    status VARCHAR(20) NOT NULL, -- 'Present', 'HalfDay', 'Absent', 'Late'
    total_hours DECIMAL(4, 2) NOT NULL DEFAULT 0.00,
    is_late BOOLEAN NOT NULL DEFAULT FALSE,
    qr_verified BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (employee_id) REFERENCES employees_employee(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_date (employee_id, date)
);

CREATE TABLE IF NOT EXISTS attendance_attendancecorrection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_id INT NOT NULL,
    requested_check_in DATETIME NOT NULL,
    requested_check_out DATETIME NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
    reviewed_by_id INT NULL,
    reviewed_at DATETIME NULL,
    FOREIGN KEY (attendance_id) REFERENCES attendance_attendance(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by_id) REFERENCES accounts_user(id) ON DELETE SET NULL
);

-- 4. Leaves: types, applications, and balances
CREATE TABLE IF NOT EXISTS leaves_leavetype (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    max_days_per_year INT NOT NULL DEFAULT 12,
    is_paid BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS leaves_leavebalance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    leave_type_id INT NOT NULL,
    year INT NOT NULL,
    allocated_days DECIMAL(4, 1) NOT NULL DEFAULT 0.0,
    used_days DECIMAL(4, 1) NOT NULL DEFAULT 0.0,
    FOREIGN KEY (employee_id) REFERENCES employees_employee(id) ON DELETE CASCADE,
    FOREIGN KEY (leave_type_id) REFERENCES leaves_leavetype(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_leave_year (employee_id, leave_type_id, year)
);

CREATE TABLE IF NOT EXISTS leaves_leave (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    leave_type_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
    manager_approved_by_id INT NULL,
    manager_approval_date DATETIME NULL,
    hr_approved_by_id INT NULL,
    hr_approval_date DATETIME NULL,
    FOREIGN KEY (employee_id) REFERENCES employees_employee(id) ON DELETE CASCADE,
    FOREIGN KEY (leave_type_id) REFERENCES leaves_leavetype(id) ON DELETE CASCADE,
    FOREIGN KEY (manager_approved_by_id) REFERENCES accounts_user(id) ON DELETE SET NULL,
    FOREIGN KEY (hr_approved_by_id) REFERENCES accounts_user(id) ON DELETE SET NULL
);

-- 5. Payroll: Periods, Adjustments, and Registers
CREATE TABLE IF NOT EXISTS payroll_payrollperiod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- e.g. "June 2026"
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    locked_at DATETIME NULL,
    locked_by_id INT NULL,
    FOREIGN KEY (locked_by_id) REFERENCES accounts_user(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS payroll_payrolladjustment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    period_id INT NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'Allowance', 'Deduction'
    name VARCHAR(100) NOT NULL, -- e.g. "Project Performance Bonus" or "Damaged Asset Penalty"
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    description TEXT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees_employee(id) ON DELETE CASCADE,
    FOREIGN KEY (period_id) REFERENCES payroll_payrollperiod(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payroll_holiday (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date DATE NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS payroll_payroll (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    period_id INT NOT NULL,
    basic_salary DECIMAL(10, 2) NOT NULL,
    hra DECIMAL(10, 2) NOT NULL,
    da DECIMAL(10, 2) NOT NULL,
    travel_allowance DECIMAL(10, 2) NOT NULL,
    medical_allowance DECIMAL(10, 2) NOT NULL,
    bonus DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    overtime_pay DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    pf_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    esi_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    professional_tax DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    income_tax DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    leave_deductions DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    late_penalties DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    other_adjustments DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    net_salary DECIMAL(10, 2) NOT NULL,
    processed_at DATETIME NOT NULL,
    processed_by_id INT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees_employee(id) ON DELETE CASCADE,
    FOREIGN KEY (period_id) REFERENCES payroll_payrollperiod(id) ON DELETE CASCADE,
    FOREIGN KEY (processed_by_id) REFERENCES accounts_user(id) ON DELETE SET NULL,
    UNIQUE KEY unique_employee_period (employee_id, period_id)
);

-- 6. Payslips: PDF Reference and sent status
CREATE TABLE IF NOT EXISTS payslips_payslip (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payroll_id INT NOT NULL UNIQUE,
    payslip_code VARCHAR(30) NOT NULL UNIQUE,
    pdf_file VARCHAR(100) NULL, -- Path to file
    is_email_sent BOOLEAN NOT NULL DEFAULT FALSE,
    sent_at DATETIME NULL,
    FOREIGN KEY (payroll_id) REFERENCES payroll_payroll(id) ON DELETE CASCADE
);

-- 7. Core: Audit Log and Settings
CREATE TABLE IF NOT EXISTS core_auditlog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(50) NOT NULL, -- e.g. "CREATE", "UPDATE", "DELETE"
    model_name VARCHAR(100) NOT NULL,
    object_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    ip_address VARCHAR(45) NULL,
    old_value JSON NULL,
    new_value JSON NULL,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS core_systemsetting (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(50) NOT NULL UNIQUE,
    value VARCHAR(255) NOT NULL,
    description TEXT NULL
);

CREATE TABLE IF NOT EXISTS core_notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id) ON DELETE CASCADE
);
