import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/university_db"

fake = Faker()
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("🚀 Starting fake data generation...")

# Clear existing data
print("🗑️  Clearing existing data...")
tables = ['placements', 'grades', 'attendance', 'enrollments', 'courses', 'students', 'hostels', 'departments']
for table in tables:
    cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
conn.commit()

# 1. Generate Departments
print("📚 Generating departments...")
departments = [
    ("Computer Science", "Dr. Rajesh Kumar", "Block A"),
    ("Electrical Engineering", "Dr. Priya Sharma", "Block B"),
    ("Mechanical Engineering", "Dr. Amit Patel", "Block C"),
    ("Civil Engineering", "Dr. Sunita Reddy", "Block D"),
    ("Information Technology", "Dr. Vijay Singh", "Block A"),
    ("Electronics", "Dr. Meera Iyer", "Block B"),
]

for dept in departments:
    cursor.execute(
        "INSERT INTO departments (name, hod_name, building) VALUES (%s, %s, %s)",
        dept
    )
conn.commit()
print(f"✅ Created {len(departments)} departments")

# 2. Generate Hostels
print("🏠 Generating hostels...")
hostels = [
    ("Aryabhata Hostel", 200, "Mr. Ramesh Verma"),
    ("Bhaskara Hostel", 180, "Ms. Lakshmi Nair"),
    ("Chanakya Hostel", 220, "Mr. Suresh Menon"),
    ("Gargi Hostel", 150, "Ms. Anita Das"),
]

for hostel in hostels:
    cursor.execute(
        "INSERT INTO hostels (name, capacity, warden_name) VALUES (%s, %s, %s)",
        hostel
    )
conn.commit()
print(f"✅ Created {len(hostels)} hostels")

# 3. Generate Students
print("👨‍🎓 Generating students...")
students_count = 500
current_year = datetime.now().year

for i in range(1, students_count + 1):
    roll_number = f"2021CS{i:04d}"
    name = fake.name()
    email = f"student{i}@university.edu"
    phone = fake.phone_number()[:15]
    department_id = random.randint(1, len(departments))
    hostel_id = random.randint(1, len(hostels))
    gpa = round(random.uniform(2.0, 4.0), 2)
    admission_year = random.choice([2020, 2021, 2022, 2023])
    
    cursor.execute("""
        INSERT INTO students (roll_number, name, email, phone, department_id, hostel_id, gpa, admission_year)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (roll_number, name, email, phone, department_id, hostel_id, gpa, admission_year))

conn.commit()
print(f"✅ Created {students_count} students")

# 4. Generate Courses
print("📖 Generating courses...")
courses = [
    ("CS101", "Data Structures", 4, 1, 1),
    ("CS102", "Algorithms", 4, 1, 2),
    ("CS201", "Database Systems", 3, 1, 3),
    ("CS202", "Operating Systems", 4, 1, 4),
    ("EE101", "Circuit Theory", 4, 2, 1),
    ("EE102", "Digital Electronics", 3, 2, 2),
    ("ME101", "Thermodynamics", 4, 3, 1),
    ("ME102", "Fluid Mechanics", 3, 3, 2),
    ("CE101", "Structural Analysis", 4, 4, 1),
    ("IT101", "Web Technologies", 3, 5, 1),
]

for course in courses:
    cursor.execute("""
        INSERT INTO courses (course_code, course_name, credits, department_id, semester)
        VALUES (%s, %s, %s, %s, %s)
    """, course)

conn.commit()
print(f"✅ Created {len(courses)} courses")

# 5. Generate Enrollments
print("📝 Generating enrollments...")
cursor.execute("SELECT id FROM students")
student_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM courses")
course_ids = [row[0] for row in cursor.fetchall()]

enrollments_count = 0
for student_id in student_ids:
    # Each student enrolls in 4-6 random courses
    num_courses = random.randint(4, 6)
    selected_courses = random.sample(course_ids, num_courses)
    
    for course_id in selected_courses:
        cursor.execute("""
            INSERT INTO enrollments (student_id, course_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (student_id, course_id))
        enrollments_count += 1

conn.commit()
print(f"✅ Created {enrollments_count} enrollments")

# 6. Generate Attendance
print("📅 Generating attendance records...")
cursor.execute("SELECT student_id, course_id FROM enrollments")
enrollments = cursor.fetchall()

# Generate attendance for last 90 days
start_date = datetime.now() - timedelta(days=90)
attendance_count = 0

for student_id, course_id in enrollments:
    for day in range(90):
        date = start_date + timedelta(days=day)
        # Skip weekends
        if date.weekday() < 5:  # Monday-Friday
            present = random.choices([True, False], weights=[0.8, 0.2])[0]  # 80% attendance rate
            
            cursor.execute("""
                INSERT INTO attendance (student_id, course_id, date, present)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (student_id, course_id, date, present))
            attendance_count += 1

conn.commit()
print(f"✅ Created {attendance_count} attendance records")

# 7. Generate Grades
print("📊 Generating grades...")
grade_mapping = {
    (90, 100): 'A+',
    (80, 89): 'A',
    (70, 79): 'B+',
    (60, 69): 'B',
    (50, 59): 'C',
    (0, 49): 'F'
}

def get_grade(score):
    for (min_score, max_score), grade in grade_mapping.items():
        if min_score <= score <= max_score:
            return grade
    return 'F'

grades_count = 0
for student_id, course_id in enrollments:
    # Generate grades for Midterm and Final
    for exam_type in ['Midterm', 'Final']:
        score = round(random.uniform(40, 100), 2)
        grade = get_grade(score)
        exam_date = fake.date_between(start_date='-6m', end_date='today')
        
        cursor.execute("""
            INSERT INTO grades (student_id, course_id, exam_type, score, grade, exam_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, course_id, exam_type, score, grade, exam_date))
        grades_count += 1

conn.commit()
print(f"✅ Created {grades_count} grade records")

# 8. Generate Placements
print("💼 Generating placements...")
companies = [
    "Google", "Microsoft", "Amazon", "Apple", "Facebook", 
    "Infosys", "TCS", "Wipro", "Cognizant", "Accenture"
]

job_roles = [
    "Software Engineer", "Data Scientist", "DevOps Engineer", 
    "Product Manager", "Business Analyst"
]

# 30% of students get placed
placed_students = random.sample(student_ids, int(0.3 * len(student_ids)))

placements_count = 0
for student_id in placed_students:
    company = random.choice(companies)
    role = random.choice(job_roles)
    package = round(random.uniform(3.5, 25.0), 2)  # 3.5 to 25 lakhs
    placement_date = fake.date_between(start_date='-1y', end_date='today')
    
    cursor.execute("""
        INSERT INTO placements (student_id, company_name, job_role, package, placement_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (student_id, company, role, package, placement_date))
    placements_count += 1

conn.commit()
print(f"✅ Created {placements_count} placement records")

# Close connection
cursor.close()
conn.close()

print("\n🎉 Fake data generation completed successfully!")
print(f"""
📊 Summary:
- Departments: {len(departments)}
- Hostels: {len(hostels)}
- Students: {students_count}
- Courses: {len(courses)}
- Enrollments: {enrollments_count}
- Attendance Records: {attendance_count}
- Grades: {grades_count}
- Placements: {placements_count}
""")
