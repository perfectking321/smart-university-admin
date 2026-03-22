import { Student, Department } from './types';

export const MOCK_STUDENTS: Student[] = [
  { id: 1, name: 'Sneha Pillai', roll_number: 'RA2301001CS004', department: 'Computer Science', gpa: 3.8, attendance_percentage: 70.0 },
  { id: 2, name: 'Grsehie Awnem', roll_number: 'RA2301001CS005', department: 'Computer Science', gpa: 3.5, attendance_percentage: 70.0 },
  { id: 3, name: 'Rahul Sharma', roll_number: 'RA2301001CS006', department: 'Electrical Engineering', gpa: 3.9, attendance_percentage: 85.0 },
  { id: 4, name: 'Priya Das', roll_number: 'RA2301001CS007', department: 'Mechanical Engineering', gpa: 3.2, attendance_percentage: 65.0 },
  { id: 5, name: 'Amit Kumar', roll_number: 'RA2301001CS008', department: 'Computer Science', gpa: 3.7, attendance_percentage: 92.0 },
];

export const MOCK_DEPARTMENTS: Department[] = [
  { id: 1, name: 'Computer Science', head: 'Dr. Alan Turing' },
  { id: 2, name: 'Electrical Engineering', head: 'Dr. Nikola Tesla' },
  { id: 3, name: 'Mechanical Engineering', head: 'Dr. James Watt' },
];

export const UNIVERSITY_SCHEMA = `
Table: students
Columns: id (INT), name (VARCHAR), roll_number (VARCHAR), department (VARCHAR), gpa (FLOAT), attendance_percentage (FLOAT)

Table: departments
Columns: id (INT), name (VARCHAR), head (VARCHAR)
`;
