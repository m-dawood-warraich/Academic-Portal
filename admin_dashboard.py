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

        header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="Admin Control Panel", font=HEADER_FONT, fg="white", bg=PRIMARY_COLOR).pack(side=tk.LEFT, padx=20)
        tk.Label(header, text=f"Logged in as: {full_name}", font=NORMAL_FONT, fg="white", bg=PRIMARY_COLOR).pack(side=tk.RIGHT, padx=20)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_students_tab()
        self.create_faculty_tab()
        self.create_courses_tab()
        self.create_reports_tab()

        logout_frame = tk.Frame(self.root, bg=BG_COLOR)
        logout_frame.pack(fill=tk.X, pady=10)
        tk.Button(logout_frame, text="🚪 Logout", bg=SECONDARY_COLOR, fg="white", font=BUTTON_FONT, 
                  padx=20, pady=5, cursor="hand2", command=self.logout).pack()
##Dynamically creates a labeled entry form
    ## Reduces redundant code in each tab
    def _build_form(self, parent, fields):
        """Helper to reduce repetitive UI code."""
        form = tk.LabelFrame(parent, text=f"Add New Entry", padx=10, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)
        entries = {}
        for i, f in enumerate(fields):
            tk.Label(form, text=f).grid(row=i, column=0, sticky=tk.W)
            e = tk.Entry(form)
            e.grid(row=i, column=1, padx=5, pady=2)
            entries[f] = e
        return form, entries
# ui setup Creating the Treeview to display student records
    def create_students_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Students")
        self.student_tree = ttk.Treeview(tab, columns=("ID", "Name", "Email", "Program", "Batch", "CGPA"), show="headings", height=15)
        for col in self.student_tree['columns']:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form, entries = self._build_form(tab, ["Username", "Password", "Full Name", "Email", "Student ID", "Batch", "Program", "CGPA"])
        def add():
            try:
                add_student(*[entries[f].get() for f in ["Username", "Password", "Full Name", "Email", "Student ID", "Batch", "Program"]], float(entries["CGPA"].get()))
                messagebox.showinfo("Success", "Student added")
                self.refresh_students()
            except Exception as ex: messagebox.showerror("Error", str(ex))
        ttk.Button(form, text="Add Student", command=add).grid(row=8, columnspan=2, pady=10)
        ttk.Button(tab, text="Delete Selected Student", command=self.delete_student).pack(pady=5)
        self.refresh_students()

    def create_faculty_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Faculty")
        self.faculty_tree = ttk.Treeview(tab, columns=("ID", "Name", "Email", "Department"), show="headings")
        self.faculty_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        form, entries = self._build_form(tab, ["Username", "Password", "Full Name", "Email", "Department", "Hire Date (YYYY-MM-DD)", "Office"])
        ttk.Button(form, text="Add Faculty", command=lambda: [add_faculty(*[entries[f].get() for f in entries]), self.refresh_faculty()]).grid(row=7, columnspan=2, pady=10)
        self.refresh_faculty()

    def create_courses_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Courses")
        self.course_tree = ttk.Treeview(tab, columns=("ID", "Code", "Name", "Credits", "Schedule"), show="headings")
        self.course_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        form, entries = self._build_form(tab, ["Course Code", "Course Name", "Credits", "Faculty ID", "Schedule"])
        ttk.Button(form, text="Add Course", command=self.refresh_courses).grid(row=5, columnspan=2, pady=10)
        self.refresh_courses()

##Refreshes the treeview to sync with the database state
    def refresh_students(self):
        for item in self.student_tree.get_children(): self.student_tree.delete(item)
        for s in get_all_students(): self.student_tree.insert("", tk.END, values=s)

    def delete_student(self):
        selected = self.student_tree.selection()
        if not selected: return messagebox.showerror("Error", "Select a student")
        student_id = self.student_tree.item(selected[0])['values'][0]
        conn = get_connection()
        row = conn.cursor().execute("SELECT user_id FROM users WHERE student_id=?", (student_id,)).fetchone()
        conn.close()
        if row: delete_user(row[0], "student"); self.refresh_students(); messagebox.showinfo("Success", "Student deleted")

    def refresh_faculty(self):
        for item in self.faculty_tree.get_children(): self.faculty_tree.delete(item)
        for f in get_all_faculty(): self.faculty_tree.insert("", tk.END, values=f)

    def refresh_courses(self):
        for item in self.course_tree.get_children(): self.course_tree.delete(item)
        for c in get_all_courses(): self.course_tree.insert("", tk.END, values=c)

    
    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        s, f, c = get_system_stats()
        tk.Label(tab, text=f"Total Students: {s}\nTotal Faculty: {f}\nTotal Courses: {c}", font=("Courier", 12), bg="white").pack(padx=20, pady=20, anchor=tk.W)

    
    def logout(self):
        self.root.destroy()
        self.login_window.show()
