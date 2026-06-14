import sqlite3
import hashlib
from datetime import datetime, timedelta
import random

DB_PATH = "academic_portal.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Create tables (same as before)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        full_name TEXT,
        email TEXT,
        student_id TEXT UNIQUE,
        batch TEXT,
        program TEXT,
        cgpa REAL,
        advisor_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS faculty (
        faculty_id INTEGER PRIMARY KEY,
        department TEXT,
        hire_date TEXT,
        office TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE,
        course_name TEXT,
        credits INTEGER,
        faculty_id INTEGER,
        schedule TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        course_id INTEGER,
        semester TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        course_id INTEGER,
        date TEXT,
        status TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        course_id INTEGER,
        grade TEXT,
        gpa REAL,
        semester TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        description TEXT,
        due_date TEXT,
        max_score INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        student_id TEXT,
        submission_date TEXT,
        file_path TEXT,
        score INTEGER,
        feedback TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        announcement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        date TEXT,
        category TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        request_no TEXT,
        req_type TEXT,
        sub_type TEXT,
        description TEXT,
        status TEXT,
        submission_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        day TEXT,
        course_code TEXT,
        course_name TEXT,
        faculty TEXT,
        type TEXT,
        start_time TEXT,
        end_time TEXT,
        room TEXT
    )''')

    # Check if we already have data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        conn.commit()
        conn.close()
        return  # Data already exists – do nothing

    # ----- Insert sample data (only if tables are empty) -----

    # Admin
    c.execute("INSERT INTO users (username, password, role, full_name, email) VALUES (?,?,?,?,?)",
              ("admin", hash_password("admin123"), "admin", "System Administrator", "admin@academic.edu"))

    # Faculty (5)
    faculty_list = [
        ("faculty1", "fac123", "Dr. Sarah Johnson", "sarah.j@academic.edu", "Computer Science", "2018-08-15", "Room 401"),
        ("faculty2", "fac123", "Prof. Michael Chen", "m.chen@academic.edu", "Computer Science", "2019-01-10", "Room 305"),
        ("faculty3", "fac123", "Dr. Emily Davis", "emily.davis@academic.edu", "Computer Science", "2020-09-01", "Room 210"),
        ("faculty4", "fac123", "Dr. Ahmed Raza", "ahmed.raza@academic.edu", "Computer Science", "2017-06-15", "Room 112"),
        ("faculty5", "fac123", "Prof. Fatima Khan", "fatima.khan@academic.edu", "Software Engineering", "2021-02-20", "Room 308")
    ]
    for f in faculty_list:
        c.execute("INSERT INTO users (username, password, role, full_name, email) VALUES (?,?,?,?,?)",
                  (f[0], hash_password(f[1]), "faculty", f[2], f[3]))
        # Get the auto-generated user_id
        user_id = c.lastrowid
        c.execute("INSERT INTO faculty (faculty_id, department, hire_date, office) VALUES (?,?,?,?)",
                  (user_id, f[4], f[5], f[6]))

    # Students (10)
    students_data = [
        ("s2024001", "pass", "Ali Raza", "ali.raza@academic.edu", "F2024001", "2024", "BS Computer Science", 3.65),
        ("s2024002", "pass", "Sara Khan", "sara.khan@academic.edu", "F2024002", "2024", "BS Computer Science", 3.42),
        ("s2024003", "pass", "Bilal Ahmed", "bilal.ahmed@academic.edu", "F2024003", "2024", "BS Computer Science", 2.98),
        ("s2024004", "pass", "Fatima Zafar", "fatima.zafar@academic.edu", "F2024004", "2024", "BS Computer Science", 3.81),
        ("s2024005", "pass", "Hamza Ali", "hamza.ali@academic.edu", "F2024005", "2024", "BS Computer Science", 3.15),
        ("s2024006", "pass", "Zainab Malik", "zainab.malik@academic.edu", "F2024006", "2024", "BS Computer Science", 3.90),
        ("s2024007", "pass", "Umar Farooq", "umar.farooq@academic.edu", "F2024007", "2024", "BS Computer Science", 2.75),
        ("s2024008", "pass", "Ayesha Naeem", "ayesha.naeem@academic.edu", "F2024008", "2024", "BS Computer Science", 3.55),
        ("s2024009", "pass", "Hassan Tariq", "hassan.tariq@academic.edu", "F2024009", "2024", "BS Computer Science", 3.22),
        ("s2024010", "pass", "Mariam Riaz", "mariam.riaz@academic.edu", "F2024010", "2024", "BS Computer Science", 3.68)
    ]
    for s in students_data:
        c.execute("INSERT INTO users (username, password, role, full_name, email, student_id, batch, program, cgpa, advisor_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (s[0], hash_password(s[1]), "student", s[2], s[3], s[4], s[5], s[6], s[7], 1))  # advisor_id = 1

    # Courses (5)
    courses_data = [
        ("CS101", "Programming Fundamentals", 3, 1, "Mon/Wed 10:00-11:30 AM"),
        ("CS201", "Data Structures", 3, 2, "Tue/Thu 2:00-3:30 PM"),
        ("CS301", "Database Systems", 3, 3, "Mon/Wed 9:00-10:30 AM"),
        ("CS401", "Operating Systems", 3, 4, "Tue/Thu 11:00-12:30 PM"),
        ("SE101", "Software Engineering", 3, 5, "Wed/Fri 1:00-2:30 PM")
    ]
    for c_data in courses_data:
        c.execute("INSERT INTO courses (course_code, course_name, credits, faculty_id, schedule) VALUES (?,?,?,?,?)", c_data)

    # Enroll all students in all courses
    c.execute("SELECT student_id FROM users WHERE role='student'")
    students = [row[0] for row in c.fetchall()]
    c.execute("SELECT course_id FROM courses")
    courses = [row[0] for row in c.fetchall()]
    for sid in students:
        for cid in courses:
            c.execute("INSERT OR IGNORE INTO enrollments (student_id, course_id, semester) VALUES (?,?,?)",
                      (sid, cid, "Spring 2026"))

    # Attendance (12 records per student per course, 80% present)
    start_date = datetime.now() - timedelta(days=40)
    for sid in students:
        for cid in courses:
            for _ in range(12):
                date = (start_date + timedelta(days=random.randint(0, 38))).strftime("%Y-%m-%d")
                status = random.choices(["Present", "Absent"], weights=[80, 20])[0]
                c.execute("INSERT INTO attendance (student_id, course_id, date, status) VALUES (?,?,?,?)",
                          (sid, cid, date, status))

    # Grades (random)
    grade_map = {"A":4.0, "A-":3.7, "B+":3.3, "B":3.0, "B-":2.7, "C+":2.3, "C":2.0}
    grades_list = list(grade_map.keys())
    for sid in students:
        for cid in courses:
            grade = random.choice(grades_list)
            gpa = grade_map[grade]
            c.execute("INSERT INTO grades (student_id, course_id, grade, gpa, semester) VALUES (?,?,?,?,?)",
                      (sid, cid, grade, gpa, "Spring 2026"))

    # Assignments
    assignments_data = [
        (1, "Assignment 1: Python Basics", "Write a calculator", "2026-06-20", 100),
        (1, "Assignment 2: Functions", "Factorial & Fibonacci", "2026-06-27", 100),
        (2, "Linked List Implementation", "Implement singly linked list", "2026-06-22", 100),
        (3, "SQL Project", "Design library database", "2026-06-28", 120),
        (4, "Process Scheduler", "Write a scheduler", "2026-07-01", 100),
        (5, "SRS Document", "Write software requirements", "2026-06-25", 80),
    ]
    for a in assignments_data:
        c.execute("INSERT INTO assignments (course_id, title, description, due_date, max_score) VALUES (?,?,?,?,?)", a)

    # Announcements
    announcements = [
        ("Midterm Exam Schedule", "Midterms: July 10-20", datetime.now().strftime("%Y-%m-%d"), "Exams"),
        ("Library Extended Hours", "Open until 10 PM", datetime.now().strftime("%Y-%m-%d"), "Library"),
        ("Guest Lecture: AI", "June 25th, 2 PM", datetime.now().strftime("%Y-%m-%d"), "Events"),
        ("Scholarship Deadline", "Apply by June 30", datetime.now().strftime("%Y-%m-%d"), "Campus News"),
    ]
    for ann in announcements:
        c.execute("INSERT INTO announcements (title, content, date, category) VALUES (?,?,?,?)", ann)

    # Sample requests
    req_types = ["Fee", "Registration", "Scholarship", "Library", "Transport"]
    sub_types = ["Installments", "Course Add/Drop", "Need-based", "Book Renewal", "Bus Pass"]
    statuses = ["PENDING", "APPROVED", "IN REVIEW"]
    for idx, sid in enumerate(students):
        req_no = f"REQ{str(idx+1).zfill(5)}"
        rt = random.choice(req_types)
        st = random.choice(sub_types)
        desc = f"Request regarding {rt} - {st}"
        status = random.choice(statuses)
        c.execute("INSERT INTO requests (student_id, request_no, req_type, sub_type, description, status, submission_date) VALUES (?,?,?,?,?,?, date('now'))",
                  (sid, req_no, rt, st, desc, status))

    # Timetable (same for all students)
    timetable_data = [
        ("Monday", "CS101", "Programming Fundamentals", "Dr. Sarah Johnson", "Theory", "10:00 AM", "11:30 AM", "Room 101"),
        ("Monday", "CS301", "Database Systems", "Dr. Emily Davis", "Theory", "1:00 PM", "2:30 PM", "Room 203"),
        ("Tuesday", "CS201", "Data Structures", "Prof. Michael Chen", "Theory", "2:00 PM", "3:30 PM", "Room 105"),
        ("Tuesday", "SE101", "Software Engineering", "Prof. Fatima Khan", "Theory", "11:00 AM", "12:30 PM", "Room 308"),
        ("Wednesday", "CS401", "Operating Systems", "Dr. Ahmed Raza", "Theory", "9:00 AM", "10:30 AM", "Room 112"),
        ("Thursday", "CS101", "Programming Fundamentals", "Dr. Sarah Johnson", "Lab", "2:00 PM", "4:00 PM", "Lab 1"),
        ("Friday", "CS301", "Database Systems", "Dr. Emily Davis", "Lab", "10:00 AM", "12:00 PM", "Lab 2"),
    ]
    for sid in students:
        for tt in timetable_data:
            c.execute("INSERT INTO timetable (student_id, day, course_code, course_name, faculty, type, start_time, end_time, room) VALUES (?,?,?,?,?,?,?,?,?)",
                      (sid, tt[0], tt[1], tt[2], tt[3], tt[4], tt[5], tt[6], tt[7]))

    conn.commit()
    conn.close()

# ---------- Helper functions (unchanged from before) ----------
def authenticate(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, role, full_name, student_id FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def get_student_details(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT full_name, program, batch, cgpa, student_id, advisor_id FROM users WHERE student_id=?", (student_id,))
    data = c.fetchone()
    if data:
        advisor_id = data[5]
        c.execute("SELECT full_name, email FROM users WHERE user_id=? AND role='faculty'", (advisor_id,))
        advisor = c.fetchone()
        data = data[:5] + advisor if advisor else data[:5] + ("None", "None")
    conn.close()
    return data

def get_registered_courses(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT c.course_code, c.course_name, c.credits, c.schedule, u.full_name
                 FROM enrollments e
                 JOIN courses c ON e.course_id = c.course_id
                 JOIN faculty f ON c.faculty_id = f.faculty_id
                 JOIN users u ON f.faculty_id = u.user_id
                 WHERE e.student_id=?''', (student_id,))
    courses = c.fetchall()
    conn.close()
    return courses

def get_student_grades(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT c.course_code, c.course_name, g.grade, g.gpa
                 FROM grades g
                 JOIN courses c ON g.course_id = c.course_id
                 WHERE g.student_id=?''', (student_id,))
    grades = c.fetchall()
    conn.close()
    return grades

def get_attendance_summary(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT c.course_code,
                        COUNT(CASE WHEN a.status='Present' THEN 1 END) as present,
                        COUNT(*) as total
                 FROM attendance a
                 JOIN courses c ON a.course_id = c.course_id
                 WHERE a.student_id=?
                 GROUP BY c.course_id''', (student_id,))
    return c.fetchall()

def get_timetable(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT day, start_time, end_time, course_code, course_name, faculty, type, room FROM timetable WHERE student_id=? ORDER BY CASE day WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 END, start_time", (student_id,))
    tt = c.fetchall()
    conn.close()
    return tt

def get_announcements_by_category(category=None):
    conn = get_connection()
    c = conn.cursor()
    if category:
        c.execute("SELECT title, content, date FROM announcements WHERE category=? ORDER BY date DESC LIMIT 10", (category,))
    else:
        c.execute("SELECT title, content, date, category FROM announcements ORDER BY date DESC LIMIT 20")
    ann = c.fetchall()
    conn.close()
    return ann

def get_all_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM announcements")
    cats = [row[0] for row in c.fetchall()]
    conn.close()
    return cats

def submit_request(student_id, req_type, sub_type, description):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM requests WHERE student_id=?", (student_id,))
    count = c.fetchone()[0] + 1
    req_no = f"REQ{str(count).zfill(5)}"
    c.execute("INSERT INTO requests (student_id, request_no, req_type, sub_type, description, status, submission_date) VALUES (?,?,?,?,?,?, date('now'))",
              (student_id, req_no, req_type, sub_type, description, "PENDING"))
    conn.commit()
    conn.close()
    return req_no

def get_student_requests(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT request_no, req_type, sub_type, description, status, submission_date FROM requests WHERE student_id=? ORDER BY submission_date DESC", (student_id,))
    reqs = c.fetchall()
    conn.close()
    return reqs

def get_assignments_for_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT a.title, a.due_date, a.max_score, c.course_code, s.score, s.feedback
                 FROM assignments a
                 JOIN courses c ON a.course_id = c.course_id
                 LEFT JOIN submissions s ON a.assignment_id = s.assignment_id AND s.student_id=?
                 WHERE c.course_id IN (SELECT course_id FROM enrollments WHERE student_id=?)''', (student_id, student_id))
    return c.fetchall()

def get_faculty_courses(faculty_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT course_id, course_code, course_name, schedule FROM courses WHERE faculty_id=?", (faculty_id,))
    return c.fetchall()

def get_students_in_course(course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT u.student_id, u.full_name
                 FROM enrollments e
                 JOIN users u ON e.student_id = u.student_id
                 WHERE e.course_id=?''', (course_id,))
    return c.fetchall()

def mark_attendance(student_id, course_id, date, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO attendance (student_id, course_id, date, status) VALUES (?,?,?,?)",
              (student_id, course_id, date, status))
    conn.commit()
    conn.close()

def update_grade(student_id, course_id, grade, gpa, semester="Spring 2026"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM grades WHERE student_id=? AND course_id=? AND semester=?", (student_id, course_id, semester))
    c.execute("INSERT INTO grades (student_id, course_id, grade, gpa, semester) VALUES (?,?,?,?,?)",
              (student_id, course_id, grade, gpa, semester))
    conn.commit()
    conn.close()

def add_assignment(course_id, title, description, due_date, max_score):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO assignments (course_id, title, description, due_date, max_score) VALUES (?,?,?,?,?)",
              (course_id, title, description, due_date, max_score))
    conn.commit()
    conn.close()

def get_all_students():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT student_id, full_name, email, program, batch, cgpa FROM users WHERE role='student'")
    return c.fetchall()

def get_all_faculty():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT u.user_id, u.full_name, u.email, f.department FROM users u JOIN faculty f ON u.user_id = f.faculty_id WHERE u.role='faculty'")
    return c.fetchall()

def get_all_courses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT course_id, course_code, course_name, credits, schedule FROM courses")
    return c.fetchall()

def add_student(username, password, full_name, email, student_id, batch, program, cgpa, advisor_id=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role, full_name, email, student_id, batch, program, cgpa, advisor_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
              (username, hash_password(password), "student", full_name, email, student_id, batch, program, cgpa, advisor_id))
    conn.commit()
    conn.close()

def add_faculty(username, password, full_name, email, department, hire_date, office):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role, full_name, email) VALUES (?,?,?,?,?)",
              (username, hash_password(password), "faculty", full_name, email))
    faculty_id = c.lastrowid
    c.execute("INSERT INTO faculty (faculty_id, department, hire_date, office) VALUES (?,?,?,?)",
              (faculty_id, department, hire_date, office))
    conn.commit()
    conn.close()
    return faculty_id

def add_course(course_code, course_name, credits, faculty_id, schedule):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO courses (course_code, course_name, credits, faculty_id, schedule) VALUES (?,?,?,?,?)",
              (course_code, course_name, credits, faculty_id, schedule))
    conn.commit()
    conn.close()

def delete_user(user_id, role):
    conn = get_connection()
    c = conn.cursor()
    if role == 'student':
        c.execute("SELECT student_id FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if row:
            student_id = row[0]
            c.execute("DELETE FROM enrollments WHERE student_id=?", (student_id,))
            c.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))
            c.execute("DELETE FROM grades WHERE student_id=?", (student_id,))
            c.execute("DELETE FROM requests WHERE student_id=?", (student_id,))
            c.execute("DELETE FROM timetable WHERE student_id=?", (student_id,))
    elif role == 'faculty':
        c.execute("UPDATE courses SET faculty_id=NULL WHERE faculty_id=?", (user_id,))
        c.execute("DELETE FROM faculty WHERE faculty_id=?", (user_id,))
    c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def enroll_student(student_id, course_id, semester="Spring 2026"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO enrollments (student_id, course_id, semester) VALUES (?,?,?)",
              (student_id, course_id, semester))
    conn.commit()
    conn.close()

def get_system_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    students = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE role='faculty'")
    faculty = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM courses")
    courses = c.fetchone()[0]
    conn.close()
    return students, faculty, courses

# Initialize database
init_db()