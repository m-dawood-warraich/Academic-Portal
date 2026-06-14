import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import *
from config import *
from scraper import get_umt_news_live, get_umt_scholarships_live, get_external_scholarships_live
import webbrowser

class StudentDashboard:
    def __init__(self, root, student_id, full_name, login_window):
        self.root = root
        self.student_id = student_id
        self.full_name = full_name
        self.login_window = login_window
        self.root.title(f"Student Portal - {full_name}")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=BG_COLOR)

        # Header
        header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=70)
        header.pack(fill=tk.X)
        tk.Label(header, text="Academic Student Portal", font=HEADER_FONT, fg="white", bg=PRIMARY_COLOR).pack(side=tk.LEFT, padx=20)
        tk.Label(header, text=f"Welcome, {full_name}", font=NORMAL_FONT, fg="white", bg=PRIMARY_COLOR).pack(side=tk.RIGHT, padx=20)

        # Main paned window
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=BG_COLOR, sashrelief=tk.RAISED, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(paned)
        paned.add(self.notebook, stretch="always")

        # Right sidebar
        right_frame = tk.Frame(paned, bg="white", width=300)
        paned.add(right_frame, width=300)

        # ========== STANDARD TABS ==========
        self.create_academic_tab()
        self.create_courses_tab()
        self.create_grades_tab()
        self.create_attendance_tab()
        self.create_timetable_tab()
        self.create_assignments_tab()
        self.create_requests_tab()

        # ========== LIVE SCRAPING TABS ==========
        self.create_news_tab()
        self.create_umt_scholarships_tab()
        self.create_external_scholarships_tab()

        # Right sidebar widgets
        self.create_advisor_card(right_frame)
        self.create_announcements_panel(right_frame)

        # Logout button
        ttk.Button(self.root, text="Logout", command=self.logout).pack(pady=5)

    # ---------- Academic Summary ----------
    def create_academic_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Academic Summary")
        details = get_student_details(self.student_id)
        if details:
            name, program, batch, cgpa, sid, advisor_name, advisor_email = details
            card = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=1)
            card.pack(fill=tk.X, padx=20, pady=20)
            metrics = [("Student Name", name), ("Student ID", sid), ("Program", program), ("Batch", batch), ("CGPA", cgpa)]
            for i, (label, value) in enumerate(metrics):
                row, col = divmod(i, 3)
                frame = tk.Frame(card, bg="white")
                frame.grid(row=row, column=col, padx=15, pady=10, sticky="w")
                tk.Label(frame, text=label, font=("Segoe UI", 9), fg="gray", bg="white").pack(anchor="w")
                tk.Label(frame, text=value, font=("Segoe UI", 12, "bold"), fg=PRIMARY_COLOR, bg="white").pack(anchor="w")

    # ---------- Registered Courses ----------
    def create_courses_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Registered Courses")
        columns = ("Code", "Course Name", "Credits", "Schedule", "Instructor")
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        courses = get_registered_courses(self.student_id)
        for c in courses:
            tree.insert("", tk.END, values=c)

    # ---------- Grades ----------
    def create_grades_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Grades")
        columns = ("Course Code", "Course Name", "Grade", "GPA")
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        grades = get_student_grades(self.student_id)
        for g in grades:
            tree.insert("", tk.END, values=g)

    # ---------- Attendance ----------
    def create_attendance_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Attendance")
        att_data = get_attendance_summary(self.student_id)
        for course_code, present, total in att_data:
            percent = (present/total*100) if total>0 else 0
            frame = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=1)
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=course_code, font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=10)
            tk.Label(frame, text=f"Present: {present}/{total} ({percent:.1f}%)", font=NORMAL_FONT, bg="white").pack(side=tk.LEFT, padx=10)
            pb = ttk.Progressbar(frame, length=200, mode='determinate', value=percent)
            pb.pack(side=tk.LEFT, padx=10)

    # ---------- Timetable ----------
    def create_timetable_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Timetable")
        columns = ("Day", "Start", "End", "Code", "Course", "Faculty", "Type", "Room")
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tt = get_timetable(self.student_id)
        for row in tt:
            tree.insert("", tk.END, values=row)

    # ---------- Assignments ----------
    def create_assignments_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Assignments")
        columns = ("Title", "Course", "Due Date", "Max Score", "My Score", "Feedback")
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        assignments = get_assignments_for_student(self.student_id)
        for a in assignments:
            tree.insert("", tk.END, values=a)
        tk.Label(tab, text="Note: Submission feature coming soon.", fg="gray").pack()

    # ---------- Support Center (Requests) ----------
    def create_requests_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Support Center")
        left = tk.Frame(tab, bg=BG_COLOR)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(left, text="Submit New Request", font=("Segoe UI", 12, "bold"), bg=BG_COLOR).pack(anchor="w")
        tk.Label(left, text="Request Type:", bg=BG_COLOR).pack(anchor="w", pady=(10,0))
        self.req_type = ttk.Combobox(left, values=["Fee", "Registration", "Scholarship", "Library", "Transport", "Other"], state="readonly")
        self.req_type.pack(fill=tk.X, pady=5)
        tk.Label(left, text="Sub Type:", bg=BG_COLOR).pack(anchor="w")
        self.sub_type = ttk.Combobox(left, values=["Installments", "Course Add/Drop", "Need-based", "Book Renewal", "Bus Pass", "General"], state="readonly")
        self.sub_type.pack(fill=tk.X, pady=5)
        tk.Label(left, text="Description:", bg=BG_COLOR).pack(anchor="w")
        self.desc_text = tk.Text(left, height=5)
        self.desc_text.pack(fill=tk.X, pady=5)
        def submit():
            rt = self.req_type.get()
            st = self.sub_type.get()
            desc = self.desc_text.get("1.0", tk.END).strip()
            if not rt or not st or not desc:
                messagebox.showerror("Error", "All fields required")
                return
            req_no = submit_request(self.student_id, rt, st, desc)
            messagebox.showinfo("Success", f"Request submitted.\nRequest No: {req_no}")
            self.desc_text.delete("1.0", tk.END)
            self.load_requests_table()
        ttk.Button(left, text="Submit Request", command=submit).pack(pady=10)

        right = tk.Frame(tab, bg=BG_COLOR)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(right, text="My Requests", font=("Segoe UI", 12, "bold"), bg=BG_COLOR).pack(anchor="w")
        columns = ("Request No", "Type", "Sub Type", "Description", "Status", "Date")
        self.req_tree = ttk.Treeview(right, columns=columns, show="headings", height=12)
        for col in columns:
            self.req_tree.heading(col, text=col)
            self.req_tree.column(col, width=120)
        self.req_tree.pack(fill=tk.BOTH, expand=True)
        self.load_requests_table()

    def load_requests_table(self):
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)
        reqs = get_student_requests(self.student_id)
        for r in reqs:
            self.req_tree.insert("", tk.END, values=r)

    # ---------- Advisor Card ----------
    def create_advisor_card(self, parent):
        card = tk.LabelFrame(parent, text="Academic Advisor", font=("Segoe UI", 10, "bold"), bg="white")
        card.pack(fill=tk.X, padx=10, pady=10)
        details = get_student_details(self.student_id)
        if details and len(details) > 5:
            advisor_name = details[5]
            advisor_email = details[6]
            tk.Label(card, text="I am your advisor", font=("Segoe UI", 9), bg="white").pack(anchor="w", padx=10, pady=(10,0))
            tk.Label(card, text=advisor_name, font=("Segoe UI", 11, "bold"), fg=PRIMARY_COLOR, bg="white").pack(anchor="w", padx=10)
            tk.Label(card, text=advisor_email, font=("Segoe UI", 9), fg="blue", bg="white").pack(anchor="w", padx=10, pady=(0,10))
        else:
            tk.Label(card, text="Advisor: Dr. Sarah Johnson", bg="white").pack(anchor="w", padx=10, pady=10)

    # ---------- Announcements Panel ----------
    def create_announcements_panel(self, parent):
        panel = tk.LabelFrame(parent, text="Announcements", font=("Segoe UI", 10, "bold"), bg="white")
        panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        cats = get_all_categories()
        cat_frame = tk.Frame(panel, bg="white")
        cat_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ann_text = scrolledtext.ScrolledText(panel, wrap=tk.WORD, height=18, font=NORMAL_FONT)
        self.ann_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for cat in cats:
            btn = tk.Button(cat_frame, text=cat, bg="white", fg=PRIMARY_COLOR, bd=0, cursor="hand2",
                            command=lambda c=cat: self.show_announcements(c))
            btn.pack(side=tk.LEFT, padx=2)
        if cats:
            self.show_announcements(cats[0])

    def show_announcements(self, category):
        self.ann_text.config(state=tk.NORMAL)
        self.ann_text.delete("1.0", tk.END)
        anns = get_announcements_by_category(category)
        for title, content, date in anns:
            self.ann_text.insert(tk.END, f"📢 {title}\n", "title")
            self.ann_text.insert(tk.END, f"{content}\n", "content")
            self.ann_text.insert(tk.END, f"📅 {date}\n\n", "date")
        self.ann_text.config(state=tk.DISABLED)
        self.ann_text.tag_config("title", font=("Segoe UI", 10, "bold"), foreground=PRIMARY_COLOR)
        self.ann_text.tag_config("content", font=NORMAL_FONT)
        self.ann_text.tag_config("date", font=("Segoe UI", 8, "italic"), foreground="gray")

    # ---------- Live News Tab (UMT) ----------
    def create_news_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📰 Live News (UMT)")
        news_frame = tk.Frame(tab)
        news_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        news_text = tk.Text(news_frame, wrap=tk.WORD, font=NORMAL_FONT, height=15)
        scrollbar = tk.Scrollbar(news_frame, orient=tk.VERTICAL, command=news_text.yview)
        news_text.config(yscrollcommand=scrollbar.set)
        news_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        news_text.insert(tk.END, "📡 Fetching latest UMT announcements...\n\n")
        news_text.config(state=tk.DISABLED)

        import threading
        def fetch_and_display():
            headlines = get_umt_news_live(12)
            news_text.config(state=tk.NORMAL)
            news_text.delete("1.0", tk.END)
            if headlines and any("Unable to fetch" in h['title'] for h in headlines):
                news_text.insert(tk.END, "⚠️ Could not load live news.\nThe website might be temporarily unavailable.\nPlease try again later.\n")
            else:
                for item in headlines:
                    news_text.insert(tk.END, f"📢 {item['title']}\n", "title")
                    news_text.insert(tk.END, f"📅 {item['date']}\n", "date")
                    if item['link']:
                        news_text.insert(tk.END, f"🔗 {item['link']}\n", "link")
                    news_text.insert(tk.END, "\n")
            news_text.config(state=tk.DISABLED)
            news_text.tag_config("title", font=("Segoe UI", 10, "bold"), foreground=PRIMARY_COLOR)
            news_text.tag_config("date", font=("Segoe UI", 9, "italic"), foreground="gray")
            news_text.tag_config("link", font=("Segoe UI", 9), foreground="blue")
        threading.Thread(target=fetch_and_display, daemon=True).start()

        refresh_btn = tk.Button(tab, text="⟳ Refresh News", bg=SECONDARY_COLOR, fg="white",
                                font=BUTTON_FONT, command=lambda: self.refresh_news_tab(news_text))
        refresh_btn.pack(pady=5)

    def refresh_news_tab(self, news_text):
        import threading
        def reload():
            headlines = get_umt_news_live(12)
            news_text.config(state=tk.NORMAL)
            news_text.delete("1.0", tk.END)
            for item in headlines:
                news_text.insert(tk.END, f"📢 {item['title']}\n", "title")
                news_text.insert(tk.END, f"📅 {item['date']}\n", "date")
                if item['link']:
                    news_text.insert(tk.END, f"🔗 {item['link']}\n", "link")
                news_text.insert(tk.END, "\n")
            news_text.config(state=tk.DISABLED)
        threading.Thread(target=reload, daemon=True).start()

    # ---------- UMT Scholarships (full clickable URL) ----------
    def create_umt_scholarships_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🏛️ UMT Scholarships")

        text_widget = tk.Text(tab, wrap=tk.WORD, font=NORMAL_FONT, height=15, cursor="hand2")
        scrollbar = tk.Scrollbar(tab, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.insert(tk.END, "📡 Loading UMT scholarship information...\n")
        text_widget.config(state=tk.DISABLED)

        import threading
        def fetch():
            scholarships = get_umt_scholarships_live()
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            if not scholarships:
                text_widget.insert(tk.END, "No scholarship data available at this time.\n")
            else:
                for idx, sch in enumerate(scholarships):
                    text_widget.insert(tk.END, f"{idx+1}. {sch['title']}\n")
                    if sch.get('description'):
                        text_widget.insert(tk.END, f"   {sch['description'][:100]}…\n")
                    link = sch.get('link', '')
                    if link and link != '#':
                        link_start = text_widget.index(tk.END)
                        text_widget.insert(tk.END, f"   {link}\n", ('link', link))
                        link_end = text_widget.index(tk.END)
                        text_widget.tag_add('link', link_start, link_end)
                        text_widget.tag_config('link', foreground='blue', underline=True)
                        text_widget.tag_bind('link', '<Button-1>', lambda e, u=link: webbrowser.open(u))
                    text_widget.insert(tk.END, "\n")
            text_widget.config(state=tk.DISABLED)
        threading.Thread(target=fetch, daemon=True).start()

    # ---------- External Scholarships (full clickable URL) ----------
    def create_external_scholarships_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🌍 External Scholarships")

        text_widget = tk.Text(tab, wrap=tk.WORD, font=NORMAL_FONT, height=15, cursor="hand2")
        scrollbar = tk.Scrollbar(tab, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.insert(tk.END, "📡 Fetching latest scholarships from HEC and TopUniversities...\n")
        text_widget.config(state=tk.DISABLED)

        import threading
        def fetch():
            scholarships = get_external_scholarships_live()
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            if not scholarships:
                text_widget.insert(tk.END, "No external scholarships found at this time.\n")
            else:
                for idx, sch in enumerate(scholarships):
                    text_widget.insert(tk.END, f"{idx+1}. {sch['title']}\n")
                    if sch.get('description'):
                        text_widget.insert(tk.END, f"   {sch['description'][:120]}…\n")
                    link = sch.get('link', '')
                    if link and link != '#':
                        link_start = text_widget.index(tk.END)
                        text_widget.insert(tk.END, f"   {link}\n", ('link', link))
                        link_end = text_widget.index(tk.END)
                        text_widget.tag_add('link', link_start, link_end)
                        text_widget.tag_config('link', foreground='blue', underline=True)
                        text_widget.tag_bind('link', '<Button-1>', lambda e, u=link: webbrowser.open(u))
                    text_widget.insert(tk.END, "\n")
            text_widget.config(state=tk.DISABLED)
        threading.Thread(target=fetch, daemon=True).start()

    # ---------- Logout ----------
    def logout(self):
        self.root.destroy()
        self.login_window.show()