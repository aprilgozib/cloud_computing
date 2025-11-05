-- Create the students table first
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    module_code VARCHAR(10) NOT NULL
);

-- Create index on module_code
CREATE INDEX IF NOT EXISTS idx_students_module_code ON students(module_code);

-- Insert initial student data
INSERT INTO students (student_id, first_name, last_name, module_code) VALUES
(1, 'John', 'Doe', 'COMP30520'),
(2, 'Jane', 'Smith', 'COMP30520'), 
(3, 'Bob', 'Johnson', 'COMP30670'),
(4, 'Alice', 'Brown', 'COMP30520'),
(5, 'Charlie', 'Wilson', 'COMP30670')
ON CONFLICT (student_id) DO NOTHING;