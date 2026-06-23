import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import *
from config import *

class FacultyDashboard:
    def __init__(self, root, faculty_id, full_name, login_window):
        self.root = root
        self.faculty_id = faculty_id
        self.full_name = full_name
        self.login_window = login_window
        self.root.title(f"Faculty Portal - {full_name}")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=BG_COLOR)

        tk.Label(self.root, text="Faculty Dashboard", font=HEADER_FONT, bg=PRIMARY_COLOR, fg="white").pack(fill=tk.X, ipady=10)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_courses_tab()
        self.create_attendance_tab()
        self.create_grades_tab()
        self.create_assignments_tab()

        ttk.Button(self.root, text="Logout", command=self.logout).pack(pady=5)

    def create_courses_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="My Courses")
        courses = get_faculty_courses(self.faculty_id)
        columns = ("ID", "Code", "Name", "Schedule")
        tree = ttk.Treeview(tab, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for c in courses:
            tree.insert("", tk.END, values=c)
        tk.Label(tab, text="Use other tabs to manage attendance, grades, and assignments.", font=NORMAL_FONT).pack()

    def create_attendance_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Mark Attendance")
        tk.Label(tab, text="Select Course:").pack(pady=5)
        courses = get_faculty_courses(self.faculty_id)
        self.att_course_combo = ttk.Combobox(tab, values=[f"{c[1]} - {c[2]}" for c in courses], state="readonly")
        self.att_course_combo.pack(pady=5)
        self.att_course_combo.bind("<<ComboboxSelected>>", self.load_attendance_students)
        self.att_frame = tk.Frame(tab)
        self.att_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.att_checkboxes = {}

    def load_attendance_students(self, event):
        for widget in self.att_frame.winfo_children():
            widget.destroy()
        self.att_checkboxes.clear()
        selected = self.att_course_combo.get()
        courses = get_faculty_courses(self.faculty_id)
        course_id = None
        for c in courses:
            if f"{c[1]} - {c[2]}" == selected:
                course_id = c[0]
                break
        if not course_id:
            return
        students = get_students_in_course(course_id)
        tk.Label(self.att_frame, text="Mark attendance for today:").pack(anchor=tk.W)
        for s in students:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.att_frame, text=s[1], variable=var)
            chk.pack(anchor=tk.W)
            self.att_checkboxes[s[0]] = var
        def save():
            date_today = datetime.now().strftime("%Y-%m-%d")
            for sid, var in self.att_checkboxes.items():
                status = "Present" if var.get() else "Absent"
                mark_attendance(sid, course_id, date_today, status)
            messagebox.showinfo("Success", "Attendance saved")
        ttk.Button(self.att_frame, text="Save Attendance", command=save).pack(pady=10)

    def create_grades_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Grades")
        tk.Label(tab, text="Select Course:").pack(pady=5)
        courses = get_faculty_courses(self.faculty_id)
        self.grade_course_combo = ttk.Combobox(tab, values=[f"{c[1]} - {c[2]}" for c in courses], state="readonly")
        self.grade_course_combo.pack(pady=5)
        self.grade_course_combo.bind("<<ComboboxSelected>>", self.load_grade_students)
        self.grade_frame = tk.Frame(tab)
        self.grade_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.grade_entries = {}

    def load_grade_students(self, event):
        for widget in self.grade_frame.winfo_children():
            widget.destroy()
        self.grade_entries.clear()
        selected = self.grade_course_combo.get()
        courses = get_faculty_courses(self.faculty_id)
        course_id = None
        for c in courses:
            if f"{c[1]} - {c[2]}" == selected:
                course_id = c[0]
                break
        if not course_id:
            return
        students = get_students_in_course(course_id)
        tk.Label(self.grade_frame, text="Enter Grade (A, B+, etc.) and GPA:").pack(anchor=tk.W)
        for s in students:
            frame = tk.Frame(self.grade_frame)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=s[1], width=20).pack(side=tk.LEFT)
            grade_entry = tk.Entry(frame, width=8)
            grade_entry.pack(side=tk.LEFT, padx=5)
            gpa_entry = tk.Entry(frame, width=8)
            gpa_entry.pack(side=tk.LEFT, padx=5)
            self.grade_entries[s[0]] = (grade_entry, gpa_entry)
        def save():
            for sid, (ge, gpe) in self.grade_entries.items():
                grade = ge.get().strip()
                gpa_str = gpe.get().strip()
                if grade and gpa_str:
                    try:
                        gpa = float(gpa_str)
                        update_grade(sid, course_id, grade, gpa)
                    except:
                        messagebox.showerror("Error", "Invalid GPA")
                        return
            messagebox.showinfo("Success", "Grades updated")
        ttk.Button(self.grade_frame, text="Save Grades", command=save).pack(pady=10)

    
    def create_assignments_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add Assignment")
        tk.Label(tab, text="Course:").grid(row=0, column=0, padx=5, pady=5)
        courses = get_faculty_courses(self.faculty_id)
        self.ass_course_combo = ttk.Combobox(tab, values=[f"{c[1]} - {c[2]}" for c in courses], state="readonly")
        self.ass_course_combo.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(tab, text="Title:").grid(row=1, column=0, padx=5, pady=5)
        self.title_entry = tk.Entry(tab, width=40)
        self.title_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(tab, text="Description:").grid(row=2, column=0, padx=5, pady=5)
        self.desc_text = tk.Text(tab, height=5, width=40)
        self.desc_text.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(tab, text="Due Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
        self.due_entry = tk.Entry(tab)
        self.due_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(tab, text="Max Score:").grid(row=4, column=0, padx=5, pady=5)
        self.max_entry = tk.Entry(tab)
        self.max_entry.grid(row=4, column=1, padx=5, pady=5)
        def submit():
            selected = self.ass_course_combo.get()
            course_id = None
            for c in courses:
                if f"{c[1]} - {c[2]}" == selected:
                    course_id = c[0]
                    break
            if not course_id:
                messagebox.showerror("Error", "Select course")
                return
            title = self.title_entry.get()
            desc = self.desc_text.get("1.0", tk.END).strip()
            due = self.due_entry.get()
            try:
                max_score = int(self.max_entry.get())
            except:
                messagebox.showerror("Error", "Max score must be integer")
                return
            add_assignment(course_id, title, desc, due, max_score)
            messagebox.showinfo("Success", "Assignment added")
            self.title_entry.delete(0, tk.END)
            self.desc_text.delete("1.0", tk.END)
            self.due_entry.delete(0, tk.END)
            self.max_entry.delete(0, tk.END)
        ttk.Button(tab, text="Create Assignment", command=submit).grid(row=5, column=0, columnspan=2, pady=20)

    
    def logout(self):
        self.root.destroy()
        self.login_window.show()
        
