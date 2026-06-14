import tkinter as tk
from tkinter import ttk, messagebox
from database import authenticate
from student_dashboard import StudentDashboard
from faculty_dashboard import FacultyDashboard
from admin_dashboard import AdminDashboard
from config import *
import random
import string

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Academic Portal Login")
        self.root.geometry("500x500")
        self.root.configure(bg=BG_COLOR)
        self.root.eval('tk::PlaceWindow . center')

        # Generate a random security code
        self.current_code = self.generate_code()

        main_frame = tk.Frame(root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=40)

        title = tk.Label(main_frame, text="📚 Academic Portal", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=PRIMARY_COLOR)
        title.pack(pady=(0,30))

        fields_frame = tk.Frame(main_frame, bg=BG_COLOR)
        fields_frame.pack(fill=tk.X)

        # Username
        tk.Label(fields_frame, text="University ID / Email", font=NORMAL_FONT, bg=BG_COLOR, anchor="w").pack(fill=tk.X, pady=(0,5))
        self.username_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), bd=1, relief=tk.SOLID)
        self.username_entry.pack(fill=tk.X, pady=(0,15), ipady=8)

        # Password
        tk.Label(fields_frame, text="Password", font=NORMAL_FONT, bg=BG_COLOR, anchor="w").pack(fill=tk.X, pady=(0,5))
        self.password_entry = tk.Entry(fields_frame, show="•", font=("Segoe UI", 11), bd=1, relief=tk.SOLID)
        self.password_entry.pack(fill=tk.X, pady=(0,15), ipady=8)

        # Security code entry + display
        code_frame = tk.Frame(fields_frame, bg=BG_COLOR)
        code_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(code_frame, text="Security Code:", font=NORMAL_FONT, bg=BG_COLOR).pack(side=tk.LEFT)
        self.code_entry = tk.Entry(code_frame, width=10, font=("Segoe UI", 10))
        self.code_entry.pack(side=tk.LEFT, padx=10)
        self.code_label = tk.Label(code_frame, text=self.current_code, font=("Segoe UI", 10, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
        self.code_label.pack(side=tk.LEFT)

        # Sign In button
        signin_btn = tk.Button(main_frame, text="SIGN IN", bg=SECONDARY_COLOR, fg="white", font=BUTTON_FONT,
                               bd=0, padx=20, pady=10, cursor="hand2", command=self.do_login)
        signin_btn.pack(fill=tk.X, pady=20)

        # Links
        links_frame = tk.Frame(main_frame, bg=BG_COLOR)
        links_frame.pack(fill=tk.X)
        tk.Label(links_frame, text="Create New Account", fg=SECONDARY_COLOR, cursor="hand2", font=NORMAL_FONT, bg=BG_COLOR).pack(side=tk.LEFT)
        tk.Label(links_frame, text=" | ", bg=BG_COLOR).pack(side=tk.LEFT)
        tk.Label(links_frame, text="Forgot Password", fg=SECONDARY_COLOR, cursor="hand2", font=NORMAL_FONT, bg=BG_COLOR).pack(side=tk.LEFT)

        self.username_entry.bind("<Return>", lambda e: self.do_login())
        self.password_entry.bind("<Return>", lambda e: self.do_login())

    def generate_code(self):
        """Generate a random 5-character alphanumeric code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def refresh_code(self):
        """Update the security code shown on the login screen."""
        self.current_code = self.generate_code()
        self.code_label.config(text=self.current_code)

    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        user_code = self.code_entry.get().strip()

        # Verify the security code (case‑insensitive)
        if user_code.upper() != self.current_code.upper():
            messagebox.showerror("Error", "Invalid security code. Please try again.")
            self.refresh_code()          # show a new code
            self.code_entry.delete(0, tk.END)
            return

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            self.refresh_code()
            return

        user = authenticate(username, password)
        if not user:
            messagebox.showerror("Error", "Invalid credentials.\n\nTest accounts:\nAdmin: admin/admin123\nFaculty: faculty1/fac123\nStudent: s2024001/pass")
            self.refresh_code()          # new code after failed login
            self.code_entry.delete(0, tk.END)
            return

        # Login successful – hide window and open dashboard
        user_id, role, full_name, student_id = user
        self.root.withdraw()
        new_root = tk.Tk()
        if role == "student":
            StudentDashboard(new_root, student_id, full_name, self)
        elif role == "faculty":
            FacultyDashboard(new_root, user_id, full_name, self)
        elif role == "admin":
            AdminDashboard(new_root, user_id, full_name, self)
        new_root.mainloop()