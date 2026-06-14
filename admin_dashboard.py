import tkinter as tk
from tkinter import ttk, messagebox
from database import *
from config import *

class AdminDashboard:
    def __init__(self, root, admin_id, full_name, login_window):
        self.root = root
        self.admin_id = admin_id
        self.full_name = full_name
        self.login_window = login_window
        self.root.title(f"Admin Portal - {full_name}")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=BG_COLOR)

        # Header
        header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="Admin Control Panel", font=HEADER_FONT, fg="white", bg=PRIMARY_COLOR).pack(side=tk.LEFT, padx=20)
        tk.Label(header, text=f"Logged in as: {full_name}", font=NORMAL_FONT, fg="white", bg=PRIMARY_COLOR).pack(side=tk.RIGHT, padx=20)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_students_tab()
        self.create_faculty_tab()
        self.create_courses_tab()
        self.create_reports_tab()

        # Logout button frame
        logout_frame = tk.Frame(self.root, bg=BG_COLOR)
        logout_frame.pack(fill=tk.X, pady=10)
        logout_btn = tk.Button(logout_frame, text="🚪 Logout", bg=SECONDARY_COLOR, fg="white",
                               font=BUTTON_FONT, padx=20, pady=5, cursor="hand2", command=self.logout)
        logout_btn.pack()

    def create_students_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Students")
        columns = ("ID", "Name", "Email", "Program", "Batch", "CGPA")
        self.student_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_students()

        form = tk.LabelFrame(tab, text="Add New Student", padx=10, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)
        fields = ["Username", "Password", "Full Name", "Email", "Student ID", "Batch", "Program", "CGPA"]
        entries = {}
        for i, f in enumerate(fields):
            tk.Label(form, text=f).grid(row=i, column=0, sticky=tk.W)
            e = tk.Entry(form)
            e.grid(row=i, column=1, padx=5, pady=2)
            entries[f] = e
        def add():
            try:
                add_student(entries["Username"].get(), entries["Password"].get(),
                            entries["Full Name"].get(), entries["Email"].get(),
                            entries["Student ID"].get(), entries["Batch"].get(),
                            entries["Program"].get(), float(entries["CGPA"].get()))
                messagebox.showinfo("Success", "Student added")
                self.refresh_students()
                for e in entries.values():
                    e.delete(0, tk.END)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
        ttk.Button(form, text="Add Student", command=add).grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(tab, text="Delete Selected Student", command=self.delete_student).pack(pady=5)

    def refresh_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for s in get_all_students():
            self.student_tree.insert("", tk.END, values=s)

    def delete_student(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a student")
            return
        values = self.student_tree.item(selected[0])['values']
        student_id = values[0]
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE student_id=?", (student_id,))
        row = c.fetchone()
        conn.close()
        if row:
            delete_user(row[0], "student")
            self.refresh_students()
            messagebox.showinfo("Success", "Student deleted")

    def create_faculty_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Faculty")
        columns = ("ID", "Name", "Email", "Department")
        self.faculty_tree = ttk.Treeview(tab, columns=columns, show="headings")
        for col in columns:
            self.faculty_tree.heading(col, text=col)
            self.faculty_tree.column(col, width=150)
        self.faculty_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_faculty()

        form = tk.LabelFrame(tab, text="Add New Faculty", padx=10, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)
        fields = ["Username", "Password", "Full Name", "Email", "Department", "Hire Date (YYYY-MM-DD)", "Office"]
        entries = {}
        for i, f in enumerate(fields):
            tk.Label(form, text=f).grid(row=i, column=0, sticky=tk.W)
            e = tk.Entry(form)
            e.grid(row=i, column=1, padx=5, pady=2)
            entries[f] = e
        def add():
            add_faculty(entries["Username"].get(), entries["Password"].get(),
                        entries["Full Name"].get(), entries["Email"].get(),
                        entries["Department"].get(), entries["Hire Date (YYYY-MM-DD)"].get(),
                        entries["Office"].get())
            messagebox.showinfo("Success", "Faculty added")
            self.refresh_faculty()
        ttk.Button(form, text="Add Faculty", command=add).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def refresh_faculty(self):
        for item in self.faculty_tree.get_children():
            self.faculty_tree.delete(item)
        for f in get_all_faculty():
            self.faculty_tree.insert("", tk.END, values=f)

    def create_courses_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Courses")
        columns = ("ID", "Code", "Name", "Credits", "Schedule")
        self.course_tree = ttk.Treeview(tab, columns=columns, show="headings")
        for col in columns:
            self.course_tree.heading(col, text=col)
            self.course_tree.column(col, width=120)
        self.course_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_courses()

        form = tk.LabelFrame(tab, text="Add New Course", padx=10, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)
        fields = ["Course Code", "Course Name", "Credits", "Faculty ID", "Schedule"]
        entries = {}
        for i, f in enumerate(fields):
            tk.Label(form, text=f).grid(row=i, column=0, sticky=tk.W)
            e = tk.Entry(form)
            e.grid(row=i, column=1, padx=5, pady=2)
            entries[f] = e
        def add():
            try:
                add_course(entries["Course Code"].get(), entries["Course Name"].get(),
                           int(entries["Credits"].get()), int(entries["Faculty ID"].get()) if entries["Faculty ID"].get() else None,
                           entries["Schedule"].get())
                messagebox.showinfo("Success", "Course added")
                self.refresh_courses()
            except:
                messagebox.showerror("Error", "Invalid data")
        ttk.Button(form, text="Add Course", command=add).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def refresh_courses(self):
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        for c in get_all_courses():
            self.course_tree.insert("", tk.END, values=c)

    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        students, faculty, courses = get_system_stats()
        report = f"Total Students: {students}\nTotal Faculty: {faculty}\nTotal Courses: {courses}\n\nEnrollment Summary: All students enrolled in all courses for Spring 2026."
        tk.Label(tab, text=report, font=("Courier", 12), justify=tk.LEFT, bg="white").pack(padx=20, pady=20, anchor=tk.W)

    def logout(self):
        self.root.destroy()
        self.login_window.show()