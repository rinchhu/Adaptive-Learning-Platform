"""
=============================================================================
ADAPTIVE LEARNING PLATFORM (ENTERPRISE EDUCATIONAL SUITE)
=============================================================================
A modern, feature-rich educational desktop application built with Python & Tkinter.
Aligned with United Nations Sustainable Development Goal 4 (SDG 4): Quality Education.

Key Features:
- Modern Dashboard with "Continue Learning" & real-time metric cards
- Professional Sidebar & Top Navigation Bar with active student profile
- Subject & Topic Management with live search filter & completion toggle
- Interactive Learning Module with in-app Python Code Playground
- Multi-Level Randomized Quiz Engine with instant answer feedback & explanations
- Topic-Specific Rule-Based Adaptive Learning Engine
- Dedicated Bookmarks System (save & review difficult questions)
- Functional Achievements & Rewards Badges
- Detailed Learning Progress, Analytics & Canvas Bar Charts
- UN SDG 4 (Quality Education) Integration
- True Multi-Student Profile Isolation via JSON
=============================================================================
"""

import io
import json
import math
import os
import random
import sys
import time
import tkinter as tk
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from tkinter import messagebox, ttk

# ---------------------------------------------------------------------------
# PATH RESOLUTION & ASSETS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LESSONS_FILE = os.path.join(BASE_DIR, "lessons.json")
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")

# ---------------------------------------------------------------------------
# MODERN DESIGN SYSTEM & COLOR THEME
# ---------------------------------------------------------------------------
COLOR_PRIMARY = "#0F172A"       # Deep Navy (Sidebar & Top Bar)
COLOR_PRIMARY_HOVER = "#1E293B" # Navy highlight
COLOR_SECONDARY = "#4F46E5"     # Indigo / Purple Accent
COLOR_SECONDARY_HOVER = "#4338CA"
COLOR_ACCENT_TEAL = "#0D9488"   # Teal (Success / Primary Action)
COLOR_TEAL_HOVER = "#0F766E"
COLOR_TEAL_LIGHT = "#F0FDFA"    # Soft teal background
COLOR_AMBER = "#D97706"         # Amber (Warning / Medium)
COLOR_AMBER_LIGHT = "#FFFBEB"
COLOR_ROSE = "#E11D48"          # Rose (Needs Revision / Incorrect)
COLOR_ROSE_LIGHT = "#FFF1F2"
COLOR_BG = "#F8FAFC"            # Light grey / off-white workspace
COLOR_CARD = "#FFFFFF"          # Pure White cards
COLOR_BORDER = "#E2E8F0"        # Subtle slate borders
COLOR_BORDER_ACTIVE = "#6366F1" # Active border highlight
COLOR_TEXT_MAIN = "#0F172A"     # Crisp dark charcoal
COLOR_TEXT_MUTED = "#64748B"    # Slate grey for subtitles
COLOR_CODE_BG = "#0B132B"       # Dark terminal background
COLOR_CODE_FG = "#38BDF8"       # Cyan code text

TOPIC_ORDER = [
    "Variables",
    "Data Types",
    "Conditional Statements",
    "Loops",
    "Functions"
]

ACHIEVEMENT_DEFINITIONS = [
    {
        "id": "first_quiz",
        "title": "First Step",
        "icon": "🎯",
        "desc": "Completed your first adaptive quiz attempt."
    },
    {
        "id": "five_quizzes",
        "title": "Dedicated Learner",
        "icon": "🏆",
        "desc": "Attempted 5 or more quizzes across curriculum topics."
    },
    {
        "id": "python_novice",
        "title": "Python Novice",
        "icon": "🐍",
        "desc": "Completed or mastered your first curriculum topic."
    },
    {
        "id": "perfect_score",
        "title": "Flawless Score",
        "icon": "🌟",
        "desc": "Scored a perfect 100% on any adaptive quiz."
    },
    {
        "id": "three_topics",
        "title": "Curriculum Explorer",
        "icon": "📚",
        "desc": "Completed or mastered at least 3 topics."
    },
    {
        "id": "python_master",
        "title": "Python Master",
        "icon": "🎓",
        "desc": "Mastered all 5 curriculum topics at highest level."
    },
    {
        "id": "curious_mind",
        "title": "Curious Mind",
        "icon": "⭐",
        "desc": "Bookmarked a tricky question for future review."
    }
]


# ===========================================================================
# 1. DATA MANAGEMENT & MULTI-STUDENT PERSISTENCE
# ===========================================================================

def load_json(filepath, default):
    """Safely loads JSON data from disk or returns default."""
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default


def save_json(filepath, data):
    """Saves dictionary data formatted with indentation."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False


def create_empty_student_profile():
    """Generates a fresh, independent progress structure for a new student."""
    return {
        "current_difficulty": "Easy",
        "completed_topics": [],
        "last_accessed_topic": TOPIC_ORDER[0],
        "recommended_next_topic": TOPIC_ORDER[0],
        "topic_progress": {
            t: {
                "status": "Not Started",
                "attempts": 0,
                "highest_score": 0,
                "last_score": 0,
                "level": "Easy"
            } for t in TOPIC_ORDER
        },
        "quiz_history": [],
        "bookmarks": [],
        "achievements": [],
        "missed_questions": []
    }


def load_multi_student_db(filepath):
    """Loads student database with automatic migration from single-student format."""
    raw = load_json(filepath, None)
    if not raw or not isinstance(raw, dict):
        return {"active_student": None, "students": {}}

    if "students" not in raw and "topic_progress" in raw:
        legacy_name = raw.get("student_name", "Student")
        migrated = {
            "active_student": legacy_name,
            "students": {
                legacy_name: {
                    "current_difficulty": raw.get("current_difficulty", "Easy"),
                    "completed_topics": raw.get("completed_topics", []),
                    "last_accessed_topic": raw.get("recommended_next_topic", TOPIC_ORDER[0]),
                    "recommended_next_topic": raw.get("recommended_next_topic", TOPIC_ORDER[0]),
                    "topic_progress": raw.get("topic_progress", {}),
                    "quiz_history": raw.get("quiz_history", []),
                    "bookmarks": raw.get("bookmarks", []),
                    "achievements": raw.get("achievements", []),
                    "missed_questions": []
                }
            }
        }
        save_json(filepath, migrated)
        return migrated
    elif "students" not in raw:
        return {"active_student": None, "students": {}}

    return raw


# ===========================================================================
# 2. RULE-BASED ADAPTIVE LEARNING ENGINE (TOPIC-SPECIFIC)
# ===========================================================================

def evaluate_adaptive_performance(topic, score, total_q, current_topic_level, student_data):
    """
    Topic-Specific Rule-Based Adaptive Learning Engine.
    Rules:
    - Score >= 80%: Advance topic difficulty (Easy -> Medium -> Hard), mark Mastered.
    - Score 50%-79%: Maintain difficulty level, mark In Progress.
    - Score < 50%: Reduce difficulty (Hard -> Medium -> Easy), mark Needs Revision.

    Targeted Topic Recommendation:
    Recommends topics based on individual topic performance (identifying individual
    knowledge gaps) rather than arbitrarily dropping unrelated topics.
    """
    pct = round((score / total_q) * 100, 1) if total_q > 0 else 0.0
    old_level = current_topic_level
    next_level = current_topic_level
    decision = ""
    reason = ""

    # Rule 1: High Performance (>= 80%)
    if pct >= 80.0:
        if current_topic_level == "Easy":
            next_level = "Medium"
            decision = f"Difficulty for '{topic}' Promoted to Medium"
        elif current_topic_level == "Medium":
            next_level = "Hard"
            decision = f"Difficulty for '{topic}' Promoted to Hard"
        else:
            next_level = "Hard"
            decision = f"Maximum Mastery Maintained in '{topic}' (Hard Level)"
        reason = f"Excellent comprehension ({pct}%). The engine has advanced your difficulty challenge for {topic}."

    # Rule 2: Moderate Performance (50% to 79%)
    elif 50.0 <= pct < 80.0:
        next_level = current_topic_level
        decision = f"Maintain {current_topic_level} Difficulty in '{topic}'"
        reason = f"Good foundational understanding ({pct}%). Consolidating practice at {current_topic_level} level will solidify mastery."

    # Rule 3: Low Performance (< 50%)
    else:
        if current_topic_level == "Hard":
            next_level = "Medium"
            decision = f"Difficulty for '{topic}' Adjusted to Medium"
        elif current_topic_level == "Medium":
            next_level = "Easy"
            decision = f"Difficulty for '{topic}' Adjusted to Easy"
        else:
            next_level = "Easy"
            decision = f"Maintain Easy Level & Revise '{topic}'"
        reason = f"Score was {pct}%. The engine detected conceptual difficulty in {topic} and recommends reviewing study materials before retrying."

    # Targeted Topic Recommendation
    completed = set(student_data.get("completed_topics", []))
    if pct >= 80.0:
        completed.add(topic)

    # If student scored < 50%, recommend revising this specific topic
    if pct < 50.0:
        recommended_topic = topic
    else:
        # Search for any topic currently flagged as 'Needs Revision'
        topic_prog = student_data.get("topic_progress", {})
        weak_topics = [t for t, p in topic_prog.items() if p.get("status") == "Needs Revision"]
        if weak_topics:
            recommended_topic = weak_topics[0]
        else:
            # Otherwise recommend next uncompleted topic
            for t in TOPIC_ORDER:
                if t not in completed:
                    recommended_topic = t
                    break
            else:
                recommended_topic = "All Topics Mastered! (Review Mode)"

    return {
        "percentage": pct,
        "old_level": old_level,
        "new_level": next_level,
        "decision": decision,
        "reason": reason,
        "recommended_topic": recommended_topic,
        "passed": pct >= 80.0
    }


def check_and_award_achievements(student_data):
    """Checks progress triggers and returns list of newly unlocked badge titles."""
    unlocked_now = []
    achievements = set(student_data.get("achievements", []))
    quiz_hist = student_data.get("quiz_history", [])
    completed_topics = student_data.get("completed_topics", [])
    bookmarks = student_data.get("bookmarks", [])

    # Check Rule 1: First Quiz
    if len(quiz_hist) >= 1 and "first_quiz" not in achievements:
        achievements.add("first_quiz")
        unlocked_now.append("First Step")

    # Check Rule 2: 5 Quizzes
    if len(quiz_hist) >= 5 and "five_quizzes" not in achievements:
        achievements.add("five_quizzes")
        unlocked_now.append("Dedicated Learner")

    # Check Rule 3: 1 Topic Completed
    if len(completed_topics) >= 1 and "python_novice" not in achievements:
        achievements.add("python_novice")
        unlocked_now.append("Python Novice")

    # Check Rule 4: Perfect Score
    if any(q.get("percentage", 0) >= 100 for q in quiz_hist) and "perfect_score" not in achievements:
        achievements.add("perfect_score")
        unlocked_now.append("Flawless Score")

    # Check Rule 5: 3 Topics Completed
    if len(completed_topics) >= 3 and "three_topics" not in achievements:
        achievements.add("three_topics")
        unlocked_now.append("Curriculum Explorer")

    # Check Rule 6: Master All Topics
    if len(completed_topics) >= len(TOPIC_ORDER) and "python_master" not in achievements:
        achievements.add("python_master")
        unlocked_now.append("Python Master")

    # Check Rule 7: First Bookmark
    if len(bookmarks) >= 1 and "curious_mind" not in achievements:
        achievements.add("curious_mind")
        unlocked_now.append("Curious Mind")

    student_data["achievements"] = list(achievements)
    return unlocked_now


# ===========================================================================
# 3. REUSABLE CUSTOM UI WIDGETS
# ===========================================================================

class HoverButton(tk.Button):
    """Button with smooth hover background transition."""
    def __init__(self, master=None, bg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER, fg_color="#FFFFFF", **kw):
        super().__init__(master, **kw)
        self.default_bg = bg_color
        self.hover_bg = hover_color
        self.configure(
            bg=self.default_bg,
            fg=fg_color,
            activebackground=self.hover_bg,
            activeforeground=fg_color,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.default_bg))


class CircularGauge(tk.Canvas):
    """Draws a clean circular donut progress meter using native Tkinter Canvas."""
    def __init__(self, master, size=110, thickness=9, bg_color=COLOR_CARD, **kwargs):
        super().__init__(master, width=size, height=size, bg=bg_color, highlightthickness=0, **kwargs)
        self.size = size
        self.thickness = thickness
        self.cx = size / 2
        self.cy = size / 2
        self.radius = (size - thickness - 8) / 2

    def set_progress(self, percent, color=COLOR_ACCENT_TEAL, label_text="Progress"):
        self.delete("all")
        self.create_oval(
            self.cx - self.radius, self.cy - self.radius,
            self.cx + self.radius, self.cy + self.radius,
            outline="#E2E8F0", width=self.thickness
        )
        extent = -(percent / 100.0) * 359.99
        if percent > 0:
            self.create_arc(
                self.cx - self.radius, self.cy - self.radius,
                self.cx + self.radius, self.cy + self.radius,
                start=90, extent=extent, outline=color, width=self.thickness, style="arc"
            )
        self.create_text(
            self.cx, self.cy - 7,
            text=f"{int(percent)}%",
            font=("Segoe UI", 15, "bold"), fill=COLOR_TEXT_MAIN
        )
        self.create_text(
            self.cx, self.cy + 13,
            text=label_text,
            font=("Segoe UI", 8, "bold"), fill=COLOR_TEXT_MUTED
        )


# ===========================================================================
# 4. MAIN APPLICATION SUITE
# ===========================================================================

class AdaptiveLearningApp(tk.Tk):
    """Primary application controller featuring a professional sidebar architecture."""

    def __init__(self):
        super().__init__()
        self.title("Adaptive Learning Platform | UN SDG 4: Quality Education")
        self.geometry("1140x780")
        self.minsize(1020, 680)
        self.configure(bg=COLOR_BG)

        # Datasets
        self.lessons_data = load_json(LESSONS_FILE, {"subjects": [], "topics": []})
        self.questions_data = load_json(QUESTIONS_FILE, {})
        self.db = load_multi_student_db(PROGRESS_FILE)
        self.active_student = self.db.get("active_student")

        # Quiz State
        self.current_topic = TOPIC_ORDER[0]
        self.active_quiz_questions = []
        self.q_index = 0
        self.quiz_score = 0
        self.quiz_mode = "standard"  # "standard" or "missed_practice"
        self.selected_choice = tk.IntVar(value=-1)
        self.quiz_answered = False
        self.quiz_results_log = []
        self.option_cards = []

        # Topic Search Filter State
        self.topic_search_query = tk.StringVar(value="")
        self.topic_filter_tab = "all"  # "all", "completed", "pending"

        # Window Layout (Top Bar + Master Body with Sidebar + Dynamic View)
        self.top_bar_frame = None
        self.sidebar_frame = None
        self.main_content_frame = None

        self.setup_main_layout()

        # Route to appropriate initial screen
        if self.active_student and self.active_student in self.db.get("students", {}):
            self.show_dashboard()
        else:
            self.show_welcome()

    # -----------------------------------------------------------------------
    # DATA & PROFILE HELPERS
    # -----------------------------------------------------------------------
    def get_current_student_data(self):
        """Returns the isolated progress dictionary for active student."""
        if not self.active_student or self.active_student not in self.db["students"]:
            self.active_student = "Student"
            self.db["students"]["Student"] = create_empty_student_profile()
            self.db["active_student"] = "Student"
            self.save_db()

        profile = self.db["students"][self.active_student]
        if "topic_progress" not in profile:
            profile["topic_progress"] = create_empty_student_profile()["topic_progress"]
        for t in TOPIC_ORDER:
            if t not in profile["topic_progress"]:
                profile["topic_progress"][t] = {
                    "status": "Not Started", "attempts": 0, "highest_score": 0, "last_score": 0, "level": "Easy"
                }
        if "bookmarks" not in profile:
            profile["bookmarks"] = []
        if "achievements" not in profile:
            profile["achievements"] = []
        if "missed_questions" not in profile:
            profile["missed_questions"] = []
        return profile

    def save_db(self):
        """Persists multi-student database safely to progress.json."""
        self.db["active_student"] = self.active_student
        save_json(PROGRESS_FILE, self.db)

    def select_or_create_student(self, name):
        """Switches active profile to existing student or initializes fresh one."""
        clean_name = name.strip()
        if not clean_name:
            messagebox.showwarning("Input Required", "Please enter a valid student name.")
            return

        if clean_name not in self.db["students"]:
            self.db["students"][clean_name] = create_empty_student_profile()

        self.active_student = clean_name
        self.save_db()
        self.show_dashboard()

    # -----------------------------------------------------------------------
    # MASTER WINDOW LAYOUT (TOP BAR + SIDEBAR + CONTENT)
    # -----------------------------------------------------------------------
    def setup_main_layout(self):
        """Initializes permanent top navigation bar, collapsible sidebar, and content host."""
        # Clear root
        for w in self.winfo_children():
            w.destroy()

        # 1. Top Navigation Bar
        self.top_bar_frame = tk.Frame(self, bg=COLOR_PRIMARY, height=58)
        self.top_bar_frame.pack(side="top", fill="x")

        # Top Bar Brand
        brand_f = tk.Frame(self.top_bar_frame, bg=COLOR_PRIMARY, padx=20, pady=10)
        brand_f.pack(side="left")

        tk.Label(
            brand_f, text="✦ ADAPTIVE LEARNING PLATFORM",
            font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg=COLOR_PRIMARY
        ).pack(side="left")

        # Top Bar Right Profile Info
        self.top_profile_frame = tk.Frame(self.top_bar_frame, bg=COLOR_PRIMARY, padx=20)
        self.top_profile_frame.pack(side="right")

        # 2. Main Work Body (Sidebar + Content Area)
        self.work_body = tk.Frame(self, bg=COLOR_BG)
        self.work_body.pack(side="bottom", fill="both", expand=True)

        # 2A. Sidebar
        self.sidebar_frame = tk.Frame(self.work_body, bg=COLOR_PRIMARY, width=230)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # 2B. Content Area
        self.main_content_frame = tk.Frame(self.work_body, bg=COLOR_BG)
        self.main_content_frame.pack(side="right", fill="both", expand=True)

    def update_top_bar(self, breadcrumb="Dashboard"):
        """Refreshes active student badge, difficulty level, and SDG 4 pill on top bar."""
        for w in self.top_profile_frame.winfo_children():
            w.destroy()

        student_data = self.get_current_student_data()
        current_diff = student_data.get("current_difficulty", "Easy")

        # Breadcrumb
        lbl_bc = tk.Label(
            self.top_profile_frame, text=f"📍 {breadcrumb}",
            font=("Segoe UI", 9), fg="#94A3B8", bg=COLOR_PRIMARY
        )
        lbl_bc.pack(side="left", padx=(0, 20))

        # SDG 4 Tag
        sdg_tag = tk.Label(
            self.top_profile_frame, text="🌍 SDG 4: Quality Education",
            font=("Segoe UI", 8, "bold"), fg="#38BDF8", bg=COLOR_PRIMARY_HOVER,
            padx=8, pady=4
        )
        sdg_tag.pack(side="left", padx=(0, 15))

        # Student Badge
        stu_tag = tk.Label(
            self.top_profile_frame, text=f"👤 {self.active_student}",
            font=("Segoe UI", 9, "bold"), fg="#FFFFFF", bg=COLOR_PRIMARY_HOVER,
            padx=10, pady=4
        )
        stu_tag.pack(side="left", padx=(0, 8))

        # Difficulty Badge
        diff_color = COLOR_ACCENT_TEAL if current_diff == "Easy" else (COLOR_AMBER if current_diff == "Medium" else COLOR_ROSE)
        diff_tag = tk.Label(
            self.top_profile_frame, text=f"LEVEL: {current_diff.upper()}",
            font=("Segoe UI", 8, "bold"), fg="#FFFFFF", bg=diff_color,
            padx=8, pady=4
        )
        diff_tag.pack(side="left")

    def build_sidebar(self, active_tab="dashboard"):
        """Renders professional side navigation buttons with badge counters."""
        for w in self.sidebar_frame.winfo_children():
            w.destroy()

        student_data = self.get_current_student_data()
        bookmarks_count = len(student_data.get("bookmarks", []))
        achievements_count = len(student_data.get("achievements", []))

        # Menu section label
        tk.Label(
            self.sidebar_frame, text="NAVIGATION MENU",
            font=("Segoe UI", 8, "bold"), fg="#64748B", bg=COLOR_PRIMARY,
            padx=20, pady=12
        ).pack(anchor="w")

        nav_items = [
            ("📊 Dashboard", "dashboard", self.show_dashboard),
            ("📚 Subjects & Lessons", "lessons", self.show_subjects_and_topics),
            ("📝 Adaptive Quiz", "quiz_start", lambda: self.show_quiz_launcher(None)),
            (f"⭐ Bookmarks ({bookmarks_count})", "bookmarks", self.show_bookmarks),
            ("📈 Progress & Analytics", "analytics", self.show_progress_analytics),
            (f"🏆 Achievements ({achievements_count}/7)", "achievements", self.show_achievements),
            ("🌍 About SDG 4", "sdg4", self.show_sdg4),
            ("👤 Switch Student", "switch", self.show_welcome)
        ]

        for label, key, cmd in nav_items:
            is_active = (key == active_tab)
            bg = COLOR_SECONDARY if is_active else COLOR_PRIMARY
            fg = "#FFFFFF" if is_active else "#CBD5E1"
            h_bg = COLOR_SECONDARY_HOVER if is_active else COLOR_PRIMARY_HOVER

            btn = HoverButton(
                self.sidebar_frame, text=label, bg_color=bg, hover_color=h_bg, fg_color=fg,
                font=("Segoe UI", 9, "bold" if is_active else "normal"),
                anchor="w", padx=20, pady=9, command=cmd
            )
            btn.pack(fill="x", pady=1)

        # Sidebar Footer
        footer = tk.Frame(self.sidebar_frame, bg=COLOR_PRIMARY, padx=20, pady=16)
        footer.pack(side="bottom", fill="x")

        tk.Label(
            footer, text="SDG 4: Quality Education",
            font=("Segoe UI", 8, "bold"), fg="#14B8A6", bg=COLOR_PRIMARY
        ).pack(anchor="w")

        tk.Label(
            footer, text="Rule-Based Personalized Platform",
            font=("Segoe UI", 7), fg="#64748B", bg=COLOR_PRIMARY
        ).pack(anchor="w", pady=(2, 0))

    def clear_content_area(self):
        """Cleans current content area to prepare for next screen."""
        for w in self.main_content_frame.winfo_children():
            w.destroy()

    def create_scrollable_container(self):
        """Helper creating a responsive scrollable canvas for content pages."""
        canvas = tk.Canvas(self.main_content_frame, bg=COLOR_BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self.main_content_frame, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=COLOR_BG, padx=28, pady=20)

        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=body, anchor="nw", width=870)

        def on_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", on_resize)
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return body

    # =======================================================================
    # SCREEN 1: MULTI-STUDENT PROFILE SELECTOR
    # =======================================================================
    def show_welcome(self):
        """Student login and profile creation screen."""
        self.clear_content_area()
        self.update_top_bar("Student Profiles")
        self.build_sidebar(active_tab="switch")

        center = tk.Frame(self.main_content_frame, bg=COLOR_BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(center, bg=COLOR_CARD, padx=42, pady=34, relief="solid", bd=1)
        card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack()

        # SDG 4 Tag
        pill = tk.Label(
            card, text="●  UNITED NATIONS SDG 4 : QUALITY EDUCATION",
            font=("Segoe UI", 8, "bold"), fg=COLOR_ACCENT_TEAL, bg=COLOR_TEAL_LIGHT,
            padx=12, pady=4
        )
        pill.pack(pady=(0, 12))

        tk.Label(
            card, text="Student Workspace Selector",
            font=("Segoe UI", 18, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack()

        desc = (
            "Select an existing student workspace or register a new one.\n"
            "Each student has their own isolated progress, difficulty level, and scores."
        )
        tk.Label(
            card, text=desc, font=("Segoe UI", 9),
            fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, justify="center"
        ).pack(pady=(6, 16))

        # Existing Students Section
        existing_names = list(self.db.get("students", {}).keys())
        if existing_names:
            tk.Label(
                card, text="Select Existing Student Profile:",
                font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
            ).pack(anchor="w", pady=(0, 6))

            stu_box = tk.Frame(card, bg=COLOR_CARD)
            stu_box.pack(fill="x", pady=(0, 16))

            for name in existing_names:
                stu_data = self.db["students"][name]
                stu_diff = stu_data.get("current_difficulty", "Easy")
                q_count = len(stu_data.get("quiz_history", []))
                mastered_count = len(stu_data.get("completed_topics", []))

                btn_stu = HoverButton(
                    stu_box,
                    text=f"👤  {name}   [ Level: {stu_diff} | {mastered_count}/5 Mastered | {q_count} Quizzes ]",
                    font=("Segoe UI", 9, "bold"),
                    bg_color=COLOR_TEAL_LIGHT, hover_color="#CCFBF1", fg_color=COLOR_ACCENT_TEAL,
                    padx=14, pady=7,
                    command=lambda n=name: self.select_or_create_student(n)
                )
                btn_stu.pack(fill="x", pady=3)

            sep = ttk.Separator(card, orient="horizontal")
            sep.pack(fill="x", pady=14)

        # Register New Student Section
        tk.Label(
            card, text="Register New Student:",
            font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w")

        f_entry = tk.Frame(card, bg=COLOR_CARD)
        f_entry.pack(fill="x", pady=(6, 14))

        new_name_var = tk.StringVar()
        entry = tk.Entry(
            f_entry, textvariable=new_name_var, font=("Segoe UI", 11),
            bg="#F8FAFC", relief="solid", bd=1
        )
        entry.pack(fill="x", ipady=5)
        entry.focus()

        def on_add():
            val = new_name_var.get().strip()
            if not val:
                messagebox.showwarning("Notice", "Please enter a student name to register.")
                return
            self.select_or_create_student(val)

        entry.bind("<Return>", lambda e: on_add())

        btn_add = HoverButton(
            card, text="+ Create New Student Profile & Start ➔", font=("Segoe UI", 10, "bold"),
            bg_color=COLOR_ACCENT_TEAL, hover_color=COLOR_TEAL_HOVER, padx=18, pady=8,
            command=on_add
        )
        btn_add.pack(fill="x")

    # =======================================================================
    # SCREEN 2: MODERN STUDENT DASHBOARD
    # =======================================================================
    def show_dashboard(self):
        """Displays rich dashboard with Continue Learning, metrics, and topic snapshot."""
        self.clear_content_area()
        self.update_top_bar("Dashboard / Overview")
        self.build_sidebar(active_tab="dashboard")

        student_data = self.get_current_student_data()
        student_name = self.active_student
        current_level = student_data.get("current_difficulty", "Easy")
        rec_topic = student_data.get("recommended_next_topic", TOPIC_ORDER[0])
        last_topic = student_data.get("last_accessed_topic", TOPIC_ORDER[0])
        completed = student_data.get("completed_topics", [])
        quiz_hist = student_data.get("quiz_history", [])

        body = self.create_scrollable_container()

        # Hero Banner
        hero = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=18, relief="solid", bd=1)
        hero.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        hero.pack(fill="x", pady=(0, 14))

        h_left = tk.Frame(hero, bg=COLOR_CARD)
        h_left.pack(side="left", fill="x", expand=True)

        tk.Label(
            h_left, text=f"Welcome back, {student_name} 👋",
            font=("Segoe UI", 17, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w")

        tk.Label(
            h_left,
            text="Personalized Python Learning Workspace  •  UN SDG 4: Quality Education Initiative",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
        ).pack(anchor="w", pady=(2, 0))

        # Circular Gauge
        pct_mastered = round((len(completed) / len(TOPIC_ORDER)) * 100, 1)
        gauge = CircularGauge(hero, size=95, thickness=8)
        gauge.pack(side="right", padx=(10, 0))
        gauge.set_progress(pct_mastered, color=COLOR_ACCENT_TEAL, label_text="Completed")

        # 4 Metric Cards Row
        metrics_row = tk.Frame(body, bg=COLOR_BG)
        metrics_row.pack(fill="x", pady=(0, 14))

        avg_score = round(sum(q.get("percentage", 0) for q in quiz_hist) / len(quiz_hist), 1) if quiz_hist else 0.0

        def make_metric(parent, title, val, sub, color):
            c = tk.Frame(parent, bg=COLOR_CARD, padx=14, pady=12, relief="solid", bd=1)
            c.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            c.pack(side="left", fill="both", expand=True, padx=3)

            tk.Label(c, text=title, font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD).pack(anchor="w")
            tk.Label(c, text=val, font=("Segoe UI", 15, "bold"), fg=color, bg=COLOR_CARD).pack(anchor="w", pady=(2, 1))
            tk.Label(c, text=sub, font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD).pack(anchor="w")

        make_metric(metrics_row, "CURRENT LEVEL", current_level.upper(), "Adaptive Challenge", COLOR_SECONDARY)
        make_metric(metrics_row, "TOPICS COMPLETED", f"{len(completed)} / {len(TOPIC_ORDER)}", f"{int(pct_mastered)}% of Course", COLOR_ACCENT_TEAL)
        make_metric(metrics_row, "AVERAGE SCORE", f"{avg_score}%" if quiz_hist else "N/A", f"From {len(quiz_hist)} Quizzes", COLOR_SECONDARY_HOVER)
        make_metric(metrics_row, "RECOMMENDED NEXT", rec_topic, "Rule Engine Target", COLOR_AMBER)

        # "Continue Learning" & Recommendation Two-Column Section
        action_split = tk.Frame(body, bg=COLOR_BG)
        action_split.pack(fill="x", pady=(0, 14))

        # Left: Continue Learning Box
        cont_card = tk.Frame(action_split, bg=COLOR_CARD, padx=18, pady=14, relief="solid", bd=1)
        cont_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        cont_card.pack(side="left", fill="both", expand=True, padx=(0, 4))

        tk.Label(
            cont_card, text="📖 Continue Learning",
            font=("Segoe UI", 11, "bold"), fg=COLOR_SECONDARY, bg=COLOR_CARD
        ).pack(anchor="w")

        last_status = student_data["topic_progress"].get(last_topic, {}).get("status", "Not Started")
        tk.Label(
            cont_card,
            text=f"Resume your latest topic: '{last_topic}' (Status: {last_status})",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
        ).pack(anchor="w", pady=(3, 10))

        btn_cont = HoverButton(
            cont_card, text="Resume Lesson ➔", font=("Segoe UI", 9, "bold"),
            bg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER, padx=14, pady=5,
            command=lambda: self.show_lesson(last_topic)
        )
        btn_cont.pack(anchor="w")

        # Right: Adaptive Recommendation Box
        rec_card = tk.Frame(action_split, bg=COLOR_AMBER_LIGHT, padx=18, pady=14, relief="solid", bd=1)
        rec_card.configure(highlightbackground="#FCD34D", highlightthickness=1)
        rec_card.pack(side="right", fill="both", expand=True, padx=(4, 0))

        tk.Label(
            rec_card, text="🎯 Rule Engine Recommendation",
            font=("Segoe UI", 11, "bold"), fg="#92400E", bg=COLOR_AMBER_LIGHT
        ).pack(anchor="w")

        tk.Label(
            rec_card,
            text=f"Suggested next study target is '{rec_topic}' at '{current_level}' level.",
            font=("Segoe UI", 9), fg="#92400E", bg=COLOR_AMBER_LIGHT
        ).pack(anchor="w", pady=(3, 10))

        if rec_topic in TOPIC_ORDER:
            btn_rec = HoverButton(
                rec_card, text="Start Recommended ➔", font=("Segoe UI", 9, "bold"),
                bg_color=COLOR_AMBER, hover_color="#B45309", padx=14, pady=5,
                command=lambda: self.show_lesson(rec_topic)
            )
            btn_rec.pack(anchor="w")

        # Curriculum Snapshot Header
        snap_hdr = tk.Frame(body, bg=COLOR_BG)
        snap_hdr.pack(fill="x", pady=(4, 8))

        tk.Label(
            snap_hdr, text="Curriculum Modules Overview",
            font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BG
        ).pack(side="left")

        btn_view_all = tk.Button(
            snap_hdr, text="Browse All Lessons ➔", font=("Segoe UI", 9, "bold"),
            fg=COLOR_SECONDARY, bg=COLOR_BG, bd=0, cursor="hand2",
            command=self.show_subjects_and_topics
        )
        btn_view_all.pack(side="right")

        # Compact Topic Cards
        for topic_name in TOPIC_ORDER:
            t_data = student_data["topic_progress"].get(topic_name, {})
            status = t_data.get("status", "Not Started")
            t_level = t_data.get("level", "Easy")
            attempts = t_data.get("attempts", 0)
            high_score = t_data.get("highest_score", 0)

            t_card = tk.Frame(body, bg=COLOR_CARD, padx=14, pady=10, relief="solid", bd=1)
            t_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            t_card.pack(fill="x", pady=3)

            c_left = tk.Frame(t_card, bg=COLOR_CARD)
            c_left.pack(side="left", fill="x", expand=True)

            tk.Label(
                c_left, text=topic_name, font=("Segoe UI", 10, "bold"),
                fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
            ).pack(anchor="w")

            if status in ["Mastered", "Completed"]:
                badge_bg, badge_fg, badge_lbl = COLOR_TEAL_LIGHT, COLOR_ACCENT_TEAL, "✔ COMPLETED"
            elif status == "Needs Revision":
                badge_bg, badge_fg, badge_lbl = COLOR_ROSE_LIGHT, COLOR_ROSE, "⚠️ NEEDS REVISION"
            elif status == "In Progress":
                badge_bg, badge_fg, badge_lbl = COLOR_AMBER_LIGHT, COLOR_AMBER, "⏳ IN PROGRESS"
            else:
                badge_bg, badge_fg, badge_lbl = "#F1F5F9", COLOR_TEXT_MUTED, "○ NOT STARTED"

            meta = tk.Frame(c_left, bg=COLOR_CARD)
            meta.pack(anchor="w", pady=(2, 0))

            tk.Label(
                meta, text=badge_lbl, font=("Segoe UI", 7, "bold"),
                fg=badge_fg, bg=badge_bg, padx=6, pady=1
            ).pack(side="left", padx=(0, 8))

            tk.Label(
                meta, text=f"Target: {t_level}  |  Attempts: {attempts}  |  Best: {high_score}%",
                font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
            ).pack(side="left")

            btn_go = HoverButton(
                t_card, text="Study ➔", font=("Segoe UI", 8, "bold"),
                bg_color=COLOR_TEAL_LIGHT, hover_color="#CCFBF1", fg_color=COLOR_ACCENT_TEAL,
                padx=10, pady=4, command=lambda t=topic_name: self.show_lesson(t)
            )
            btn_go.pack(side="right")

    # =======================================================================
    # SCREEN 3: SUBJECT & TOPIC MANAGEMENT WITH LIVE SEARCH & FILTERS
    # =======================================================================
    def show_subjects_and_topics(self):
        """Browse subjects, search topics, and inspect completion status."""
        self.clear_content_area()
        self.update_top_bar("Subjects & Topics")
        self.build_sidebar(active_tab="lessons")

        student_data = self.get_current_student_data()
        body = self.create_scrollable_container()

        # Subject Title Header
        hdr = tk.Frame(body, bg=COLOR_CARD, padx=20, pady=16, relief="solid", bd=1)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 14))

        tk.Label(
            hdr, text="📚 Subject: Python Basics",
            font=("Segoe UI", 15, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Explore curriculum lessons, run executable Python code examples, and mark topics completed.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
        ).pack(anchor="w", pady=(2, 0))

        # Search & Filter Bar Card
        bar = tk.Frame(body, bg=COLOR_CARD, padx=16, pady=12, relief="solid", bd=1)
        bar.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        bar.pack(fill="x", pady=(0, 14))

        # Search Entry Box
        f_search = tk.Frame(bar, bg=COLOR_CARD)
        f_search.pack(side="left", fill="x", expand=True)

        tk.Label(f_search, text="🔍", font=("Segoe UI", 11), bg=COLOR_CARD).pack(side="left", padx=(0, 6))

        entry_search = tk.Entry(
            f_search, textvariable=self.topic_search_query, font=("Segoe UI", 10),
            bg="#F8FAFC", relief="solid", bd=1
        )
        entry_search.pack(side="left", fill="x", expand=True, ipady=4)
        entry_search.bind("<KeyRelease>", lambda e: self.render_topics_list(topics_container))

        # Filter Tabs Row
        filter_tabs = tk.Frame(bar, bg=COLOR_CARD)
        filter_tabs.pack(side="right", padx=(15, 0))

        def set_filter(mode):
            self.topic_filter_tab = mode
            self.render_topics_list(topics_container)

        for label, mode in [("All Topics", "all"), ("Completed", "completed"), ("Pending", "pending")]:
            is_active = (self.topic_filter_tab == mode)
            bg = COLOR_SECONDARY if is_active else "#F1F5F9"
            fg = "#FFFFFF" if is_active else COLOR_TEXT_MAIN
            h_bg = COLOR_SECONDARY_HOVER if is_active else "#E2E8F0"

            b = HoverButton(
                filter_tabs, text=label, bg_color=bg, hover_color=h_bg, fg_color=fg,
                font=("Segoe UI", 8, "bold"), padx=10, pady=4,
                command=lambda m=mode: set_filter(m)
            )
            b.pack(side="left", padx=2)

        # Dynamic Topics List Container
        topics_container = tk.Frame(body, bg=COLOR_BG)
        topics_container.pack(fill="both", expand=True)

        self.render_topics_list(topics_container)

    def render_topics_list(self, container):
        """Renders filtered topic cards dynamically based on search query and tab."""
        for w in container.winfo_children():
            w.destroy()

        student_data = self.get_current_student_data()
        query = self.topic_search_query.get().strip().lower()
        tab = self.topic_filter_tab
        completed_set = set(student_data.get("completed_topics", []))

        # Filter topics
        matched_topics = []
        for t in TOPIC_ORDER:
            # Query match
            if query and query not in t.lower():
                # Also search summary
                t_info = next((item for item in self.lessons_data.get("topics", []) if item.get("name") == t), None)
                summary = t_info.get("summary", "").lower() if t_info else ""
                if query not in summary:
                    continue

            # Tab filter
            is_completed = (t in completed_set)
            if tab == "completed" and not is_completed:
                continue
            if tab == "pending" and is_completed:
                continue

            matched_topics.append(t)

        if not matched_topics:
            empty_lbl = tk.Label(
                container, text="No topics found matching your filter criteria.",
                font=("Segoe UI", 10, "italic"), fg=COLOR_TEXT_MUTED, bg=COLOR_BG
            )
            empty_lbl.pack(pady=20)
            return

        for topic_name in matched_topics:
            t_info = next((item for item in self.lessons_data.get("topics", []) if item.get("name") == topic_name), None)
            summary = t_info.get("summary", "") if t_info else ""
            t_data = student_data["topic_progress"].get(topic_name, {})
            status = t_data.get("status", "Not Started")
            t_level = t_data.get("level", "Easy")
            is_completed = (topic_name in completed_set)

            card = tk.Frame(container, bg=COLOR_CARD, padx=18, pady=14, relief="solid", bd=1)
            card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            card.pack(fill="x", pady=4)

            # Left Info
            c_left = tk.Frame(card, bg=COLOR_CARD)
            c_left.pack(side="left", fill="x", expand=True)

            t_title = tk.Label(
                c_left, text=topic_name, font=("Segoe UI", 12, "bold"),
                fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
            )
            t_title.pack(anchor="w")

            if summary:
                tk.Label(
                    c_left, text=summary, font=("Segoe UI", 9),
                    fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
                ).pack(anchor="w", pady=(2, 4))

            # Status pill & Level badge
            meta = tk.Frame(c_left, bg=COLOR_CARD)
            meta.pack(anchor="w")

            if is_completed:
                badge_bg, badge_fg, badge_lbl = COLOR_TEAL_LIGHT, COLOR_ACCENT_TEAL, "✔ COMPLETED"
            elif status == "Needs Revision":
                badge_bg, badge_fg, badge_lbl = COLOR_ROSE_LIGHT, COLOR_ROSE, "⚠️ NEEDS REVISION"
            elif status == "In Progress":
                badge_bg, badge_fg, badge_lbl = COLOR_AMBER_LIGHT, COLOR_AMBER, "⏳ IN PROGRESS"
            else:
                badge_bg, badge_fg, badge_lbl = "#F1F5F9", COLOR_TEXT_MUTED, "○ NOT STARTED"

            tk.Label(
                meta, text=badge_lbl, font=("Segoe UI", 8, "bold"),
                fg=badge_fg, bg=badge_bg, padx=7, pady=2
            ).pack(side="left", padx=(0, 8))

            tk.Label(
                meta, text=f"Target Level: {t_level}",
                font=("Segoe UI", 8, "bold"), fg=COLOR_SECONDARY, bg="#EEF2FF",
                padx=6, pady=2
            ).pack(side="left")

            # Right Action Buttons
            btn_study = HoverButton(
                card, text="Read Lesson ➔", font=("Segoe UI", 9, "bold"),
                bg_color=COLOR_TEAL_LIGHT, hover_color="#CCFBF1", fg_color=COLOR_ACCENT_TEAL,
                padx=12, pady=6, command=lambda t=topic_name: self.show_lesson(t)
            )
            btn_study.pack(side="right", padx=(6, 0))

            btn_quiz = HoverButton(
                card, text="Take Quiz", font=("Segoe UI", 9),
                bg_color="#F1F5F9", hover_color="#E2E8F0", fg_color=COLOR_TEXT_MAIN,
                padx=10, pady=6, command=lambda t=topic_name: self.show_quiz_launcher(t)
            )
            btn_quiz.pack(side="right")

    # =======================================================================
    # SCREEN 4: IMPROVED LEARNING MODULE WITH CODE PLAYGROUND
    # =======================================================================
    def show_lesson(self, topic_name):
        """Displays lesson explanation, executable playground, key points, and mark completed."""
        self.clear_content_area()
        self.update_top_bar(f"Lessons / {topic_name}")
        self.build_sidebar(active_tab="lessons")
        self.current_topic = topic_name

        student_data = self.get_current_student_data()
        student_data["last_accessed_topic"] = topic_name
        self.save_db()

        t_level = student_data["topic_progress"].get(topic_name, {}).get("level", "Easy")
        topic_info = next((t for t in self.lessons_data.get("topics", []) if t.get("name") == topic_name), None)
        is_completed = (topic_name in student_data.get("completed_topics", []))

        body = self.create_scrollable_container()

        # Lesson Title Header
        hdr = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=16, relief="solid", bd=1)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 14))

        tk.Label(
            hdr, text=f"Lesson: {topic_name}",
            font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(side="left")

        diff_badge = tk.Label(
            hdr, text=f"YOUR TARGET LEVEL: {t_level.upper()}",
            font=("Segoe UI", 8, "bold"), fg="#FFFFFF", bg=COLOR_SECONDARY,
            padx=10, pady=4
        )
        diff_badge.pack(side="right")

        if not topic_info:
            tk.Label(body, text="Lesson content not found.", fg=COLOR_ROSE, bg=COLOR_BG).pack(pady=20)
            return

        # 1. Topic Introduction / Summary Card
        sum_card = tk.Frame(body, bg=COLOR_CARD, padx=20, pady=16, relief="solid", bd=1)
        sum_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        sum_card.pack(fill="x", pady=(0, 12))

        tk.Label(sum_card, text="📌 Concept Overview", font=("Segoe UI", 11, "bold"), fg=COLOR_SECONDARY, bg=COLOR_CARD).pack(anchor="w")
        tk.Label(sum_card, text=topic_info.get("summary", ""), font=("Segoe UI", 10), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, wraplength=830, justify="left").pack(anchor="w", pady=(5, 0))

        # 2. Detailed Explanation Card
        exp_card = tk.Frame(body, bg=COLOR_CARD, padx=20, pady=16, relief="solid", bd=1)
        exp_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        exp_card.pack(fill="x", pady=(0, 12))

        tk.Label(exp_card, text="📖 Detailed Explanation", font=("Segoe UI", 11, "bold"), fg=COLOR_SECONDARY, bg=COLOR_CARD).pack(anchor="w")
        tk.Label(exp_card, text=topic_info.get("explanation", ""), font=("Segoe UI", 10), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, wraplength=830, justify="left").pack(anchor="w", pady=(5, 0))

        # 3. Interactive Code Playground Card
        code_card = tk.Frame(body, bg=COLOR_CODE_BG, padx=20, pady=16, relief="solid", bd=1)
        code_card.pack(fill="x", pady=(0, 12))

        tk.Label(code_card, text="💻 Interactive Python Code Playground (Editable)", font=("Consolas", 10, "bold"), fg="#94A3B8", bg=COLOR_CODE_BG).pack(anchor="w")

        code_text = tk.Text(code_card, font=("Consolas", 10), bg="#0F172A", fg=COLOR_CODE_FG, height=8, relief="flat", insertbackground="white")
        code_text.pack(fill="x", pady=(8, 6))
        code_text.insert("1.0", topic_info.get("code_example", "# No sample available"))

        output_box = tk.Label(code_card, text="Click 'Run Code Snippet' below to execute...", font=("Consolas", 9), fg="#A5B4FC", bg="#1E293B", padx=10, pady=6, anchor="w", justify="left")
        output_box.pack(fill="x", pady=(0, 8))

        def execute_snippet():
            raw_code = code_text.get("1.0", "end-1c")
            buffer = io.StringIO()
            try:
                with redirect_stdout(buffer), redirect_stderr(buffer):
                    exec(raw_code, {"__name__": "__main__"})
                out = buffer.getvalue().strip()
                output_box.configure(text=out if out else "[Code executed successfully with no print output]", fg="#34D399")
            except Exception as err:
                output_box.configure(text=f"Error: {err}", fg="#F87171")

        btn_run = HoverButton(
            code_card, text="▶ Run Code Snippet", font=("Consolas", 9, "bold"),
            bg_color=COLOR_ACCENT_TEAL, hover_color=COLOR_TEAL_HOVER, padx=14, pady=5,
            command=execute_snippet
        )
        btn_run.pack(anchor="w")

        # 4. Key Takeaways Card
        key_card = tk.Frame(body, bg=COLOR_CARD, padx=20, pady=16, relief="solid", bd=1)
        key_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        key_card.pack(fill="x", pady=(0, 16))

        tk.Label(key_card, text="🔑 Important Points to Remember", font=("Segoe UI", 11, "bold"), fg=COLOR_SECONDARY, bg=COLOR_CARD).pack(anchor="w")
        for pt in topic_info.get("key_points", []):
            tk.Label(key_card, text=f"•  {pt}", font=("Segoe UI", 10), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, wraplength=830, justify="left").pack(anchor="w", pady=2)

        # Bottom Action Bar
        act_bar = tk.Frame(body, bg=COLOR_BG)
        act_bar.pack(fill="x", pady=10)

        btn_back = HoverButton(
            act_bar, text="⬅ Back to Topics", font=("Segoe UI", 10),
            bg_color=COLOR_CARD, hover_color="#F1F5F9", fg_color=COLOR_TEXT_MAIN,
            padx=16, pady=8, command=self.show_subjects_and_topics
        )
        btn_back.pack(side="left")

        # Mark Completed Toggle Button
        def toggle_completion():
            if topic_name in student_data["completed_topics"]:
                student_data["completed_topics"].remove(topic_name)
                student_data["topic_progress"][topic_name]["status"] = "In Progress"
                messagebox.showinfo("Status Updated", f"'{topic_name}' marked as In Progress.")
            else:
                student_data["completed_topics"].append(topic_name)
                student_data["topic_progress"][topic_name]["status"] = "Completed"
                # Check achievements
                new_badges = check_and_award_achievements(student_data)
                self.save_db()
                if new_badges:
                    messagebox.showinfo("Achievement Unlocked!", f"🎉 Unlocked new badge(s): {', '.join(new_badges)}!")
                else:
                    messagebox.showinfo("Topic Completed", f"Great job! '{topic_name}' marked as Completed.")
            self.save_db()
            self.show_lesson(topic_name)

        comp_text = "✔ Marked Completed" if is_completed else "○ Mark as Completed"
        comp_bg = COLOR_TEAL_LIGHT if is_completed else COLOR_CARD
        comp_fg = COLOR_ACCENT_TEAL if is_completed else COLOR_TEXT_MAIN

        btn_comp = HoverButton(
            act_bar, text=comp_text, font=("Segoe UI", 10, "bold"),
            bg_color=comp_bg, hover_color="#CCFBF1", fg_color=comp_fg,
            padx=16, pady=8, command=toggle_completion
        )
        btn_comp.pack(side="left", padx=10)

        btn_quiz = HoverButton(
            act_bar, text=f"Start Adaptive Quiz ({t_level}) ➔", font=("Segoe UI", 10, "bold"),
            bg_color=COLOR_ACCENT_TEAL, hover_color=COLOR_TEAL_HOVER, padx=20, pady=8,
            command=lambda: self.show_quiz_launcher(topic_name)
        )
        btn_quiz.pack(side="right")

    # =======================================================================
    # SCREEN 5: IMPROVED QUIZ SYSTEM (LAUNCHER & MODES)
    # =======================================================================
    def show_quiz_launcher(self, preselected_topic=None):
        """Displays quiz configuration: topic, difficulty, or missed questions practice."""
        self.clear_content_area()
        self.update_top_bar("Adaptive Quiz / Setup")
        self.build_sidebar(active_tab="quiz_start")

        student_data = self.get_current_student_data()
        body = self.create_scrollable_container()

        hdr = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=16, relief="solid", bd=1)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 16))

        tk.Label(
            hdr, text="📝 Adaptive Quiz Center",
            font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Test your understanding with randomized questions, instant pedagogical explanations, and rule-based adaptation.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
        ).pack(anchor="w", pady=(2, 0))

        # Card 1: Standard Adaptive Quiz
        card_std = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=18, relief="solid", bd=1)
        card_std.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_std.pack(fill="x", pady=(0, 16))

        tk.Label(
            card_std, text="1. Standard Adaptive Curriculum Quiz",
            font=("Segoe UI", 12, "bold"), fg=COLOR_SECONDARY, bg=COLOR_CARD
        ).pack(anchor="w")

        tk.Label(
            card_std,
            text="Select topic and difficulty level. Questions are randomized each session.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
        ).pack(anchor="w", pady=(2, 12))

        f_opts = tk.Frame(card_std, bg=COLOR_CARD)
        f_opts.pack(fill="x", pady=(0, 14))

        tk.Label(f_opts, text="Topic:", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD).pack(side="left")
        topic_var = tk.StringVar(value=preselected_topic if preselected_topic else TOPIC_ORDER[0])
        combo_t = ttk.Combobox(f_opts, textvariable=topic_var, values=TOPIC_ORDER, state="readonly", width=22)
        combo_t.pack(side="left", padx=(8, 25))

        # Topic specific difficulty defaults
        def update_diff_from_topic(event=None):
            chosen = topic_var.get()
            t_def_diff = student_data["topic_progress"].get(chosen, {}).get("level", "Easy")
            diff_var.set(t_def_diff)

        tk.Label(f_opts, text="Difficulty Level:", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD).pack(side="left")
        diff_var = tk.StringVar(value=student_data["topic_progress"].get(topic_var.get(), {}).get("level", "Easy"))
        combo_d = ttk.Combobox(f_opts, textvariable=diff_var, values=["Easy", "Medium", "Hard"], state="readonly", width=12)
        combo_d.pack(side="left", padx=8)

        combo_t.bind("<<ComboboxSelected>>", update_diff_from_topic)

        btn_start_std = HoverButton(
            card_std, text="Launch Adaptive Quiz ➔", font=("Segoe UI", 10, "bold"),
            bg_color=COLOR_ACCENT_TEAL, hover_color=COLOR_TEAL_HOVER, padx=18, pady=8,
            command=lambda: self.start_quiz_session(topic_var.get(), diff_var.get(), mode="standard")
        )
        btn_start_std.pack(anchor="w")

        # Card 2: Practice Missed Questions
        card_missed = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=18, relief="solid", bd=1)
        card_missed.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_missed.pack(fill="x")

        tk.Label(
            card_missed, text="2. Targeted Practice: Missed Questions",
            font=("Segoe UI", 12, "bold"), fg=COLOR_AMBER, bg=COLOR_CARD
        ).pack(anchor="w")

        missed_list = student_data.get("missed_questions", [])
        tk.Label(
            card_missed,
            text=f"You currently have {len(missed_list)} recorded question(s) that were previously answered incorrectly.\nPracticing missed questions helps reinforce difficult concepts without frustration.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, justify="left"
        ).pack(anchor="w", pady=(2, 12))

        btn_start_missed = HoverButton(
            card_missed, text=f"Practice Missed Questions ({len(missed_list)}) ➔", font=("Segoe UI", 10, "bold"),
            bg_color=COLOR_AMBER, hover_color="#B45309", padx=18, pady=8,
            command=lambda: self.start_quiz_session(None, None, mode="missed_practice")
        )
        if len(missed_list) == 0:
            btn_start_missed.configure(state="disabled", bg="#CBD5E1", fg="#94A3B8")
        btn_start_missed.pack(anchor="w")

    def start_quiz_session(self, topic_name, difficulty, mode="standard"):
        """Initializes randomized question pool and starts quiz."""
        student_data = self.get_current_student_data()
        self.quiz_mode = mode

        if mode == "missed_practice":
            missed = student_data.get("missed_questions", [])
            if not missed:
                messagebox.showinfo("No Questions", "You have no missed questions to practice!")
                return
            pool = list(missed)
            random.shuffle(pool)
            self.active_quiz_questions = pool[:min(5, len(pool))]
            self.current_topic = "Missed Questions Practice"
        else:
            self.current_topic = topic_name
            # Fetch from questions bank
            pool = self.questions_data.get(topic_name, {}).get(difficulty, [])
            if not pool:
                pool = self.questions_data.get(topic_name, {}).get("Easy", [])

            if not pool:
                messagebox.showerror("Error", f"No questions available for {topic_name}.")
                return

            randomized = list(pool)
            random.shuffle(randomized)
            self.active_quiz_questions = randomized[:min(5, len(randomized))]

            # Save topic difficulty target
            student_data["topic_progress"][topic_name]["level"] = difficulty
            self.save_db()

        self.q_index = 0
        self.quiz_score = 0
        self.quiz_results_log = []
        self.render_active_question()

    def render_active_question(self):
        """Displays one question at a time with instant feedback and bookmarking."""
        self.clear_content_area()
        self.update_top_bar(f"Quiz / {self.current_topic}")
        self.build_sidebar(active_tab="quiz_start")

        student_data = self.get_current_student_data()
        total_q = len(self.active_quiz_questions)
        q_idx = self.q_index
        q_data = self.active_quiz_questions[q_idx]
        current_diff = student_data["topic_progress"].get(self.current_topic, {}).get("level", "Easy")

        self.quiz_answered = False
        self.selected_choice.set(-1)

        body = self.create_scrollable_container()

        # Quiz Header Bar
        hdr = tk.Frame(body, bg=COLOR_BG)
        hdr.pack(fill="x", pady=(0, 10))

        tk.Label(
            hdr, text=f"Topic: {self.current_topic}",
            font=("Segoe UI", 14, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BG
        ).pack(side="left")

        diff_tag = tk.Label(
            hdr, text=f"LEVEL: {current_diff.upper()}",
            font=("Segoe UI", 8, "bold"), fg="#FFFFFF", bg=COLOR_SECONDARY,
            padx=10, pady=3
        )
        diff_tag.pack(side="right")

        # Visual Animated Progress Bar
        p_frame = tk.Frame(body, bg="#E2E8F0", height=6)
        p_frame.pack(fill="x", pady=(0, 12))

        pct_done = ((q_idx + 1) / total_q)
        fill_width = int(pct_done * 870)
        p_fill = tk.Frame(p_frame, bg=COLOR_ACCENT_TEAL, width=fill_width, height=6)
        p_fill.pack(side="left")

        # Question Subheader
        q_sub = tk.Frame(body, bg=COLOR_BG)
        q_sub.pack(fill="x", pady=(0, 6))

        tk.Label(
            q_sub, text=f"Question {q_idx + 1} of {total_q}",
            font=("Segoe UI", 10, "bold"), fg=COLOR_SECONDARY, bg=COLOR_BG
        ).pack(side="left")

        # Bookmark Check
        def is_bookmarked():
            return any(b.get("question") == q_data["question"] for b in student_data.get("bookmarks", []))

        # Bookmark Toggle Button
        btn_bm = tk.Button(
            q_sub, text="★ Bookmarked" if is_bookmarked() else "☆ Bookmark Question",
            font=("Segoe UI", 8, "bold"),
            bg="#FEF3C7" if is_bookmarked() else COLOR_CARD,
            fg="#B45309" if is_bookmarked() else COLOR_TEXT_MUTED,
            relief="solid", bd=1, padx=8, pady=2, cursor="hand2"
        )
        btn_bm.pack(side="right")

        def toggle_bm():
            if is_bookmarked():
                student_data["bookmarks"] = [b for b in student_data["bookmarks"] if b.get("question") != q_data["question"]]
                btn_bm.configure(text="☆ Bookmark Question", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED)
            else:
                student_data["bookmarks"].append({
                    "question": q_data["question"],
                    "options": q_data["options"],
                    "answer": q_data["answer"],
                    "explanation": q_data.get("explanation", ""),
                    "topic": self.current_topic,
                    "difficulty": current_diff
                })
                btn_bm.configure(text="★ Bookmarked", bg="#FEF3C7", fg="#B45309")
                check_and_award_achievements(student_data)
            self.save_db()

        btn_bm.configure(command=toggle_bm)

        # Question Card
        q_card = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=18, relief="solid", bd=1)
        q_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        q_card.pack(fill="x", pady=(0, 14))

        tk.Label(
            q_card, text=q_data["question"],
            font=("Segoe UI", 12), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD,
            wraplength=800, justify="left"
        ).pack(anchor="w")

        # Hint Strip
        hint_frame = tk.Frame(q_card, bg=COLOR_CARD)
        hint_frame.pack(anchor="w", pady=(8, 0))

        lbl_hint_txt = tk.Label(hint_frame, text="", font=("Segoe UI", 9, "italic"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)

        def show_hint():
            lbl_hint_txt.configure(text=f"💡 Hint: {q_data.get('hint', 'Analyze key principles.')}")

        btn_hint = tk.Button(
            hint_frame, text="💡 Show Hint", font=("Segoe UI", 8, "bold"),
            bg="#EEF2FF", fg=COLOR_SECONDARY, relief="flat", cursor="hand2", padx=8, pady=2,
            command=show_hint
        )
        btn_hint.pack(side="left", padx=(0, 8))
        lbl_hint_txt.pack(side="left")

        # Interactive Options Container
        options_container = tk.Frame(body, bg=COLOR_BG)
        options_container.pack(fill="x", pady=(0, 14))

        self.option_cards = []

        def select_option(opt_idx):
            if self.quiz_answered:
                return  # Prevent change after submit
            self.selected_choice.set(opt_idx)
            for idx, (frame, dot, txt) in enumerate(self.option_cards):
                if idx == opt_idx:
                    frame.configure(bg=COLOR_TEAL_LIGHT, highlightbackground=COLOR_ACCENT_TEAL, highlightthickness=2)
                    dot.configure(text="●", fg=COLOR_ACCENT_TEAL, bg=COLOR_TEAL_LIGHT)
                    txt.configure(fg=COLOR_TEXT_MAIN, bg=COLOR_TEAL_LIGHT, font=("Segoe UI", 10, "bold"))
                else:
                    frame.configure(bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
                    dot.configure(text="○", fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
                    txt.configure(fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, font=("Segoe UI", 10))

        for idx, text in enumerate(q_data["options"]):
            card = tk.Frame(options_container, bg=COLOR_CARD, padx=14, pady=10, relief="solid", bd=1)
            card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1, cursor="hand2")
            card.pack(fill="x", pady=3)

            dot = tk.Label(card, text="○", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
            dot.pack(side="left", padx=(0, 10))

            txt = tk.Label(card, text=text, font=("Segoe UI", 10), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD)
            txt.pack(side="left", fill="x", expand=True, anchor="w")

            card.bind("<Button-1>", lambda e, i=idx: select_option(i))
            dot.bind("<Button-1>", lambda e, i=idx: select_option(i))
            txt.bind("<Button-1>", lambda e, i=idx: select_option(i))

            self.option_cards.append((card, dot, txt))

        # Instant Feedback Banner Box
        feedback_box = tk.Frame(body, bg=COLOR_BG)
        feedback_box.pack(fill="x", pady=(0, 14))

        lbl_fb_title = tk.Label(feedback_box, text="", font=("Segoe UI", 10, "bold"), bg=COLOR_BG)
        lbl_fb_expl = tk.Label(feedback_box, text="", font=("Segoe UI", 9), fg=COLOR_TEXT_MAIN, bg=COLOR_BG, wraplength=800, justify="left")

        # Action Buttons Bar
        btn_bar = tk.Frame(body, bg=COLOR_BG)
        btn_bar.pack(fill="x")

        btn_cancel = HoverButton(
            btn_bar, text="Cancel Quiz", font=("Segoe UI", 9),
            bg_color=COLOR_CARD, hover_color="#F1F5F9", fg_color=COLOR_TEXT_MUTED,
            padx=14, pady=7, command=self.show_dashboard
        )
        btn_cancel.pack(side="left")

        is_last = (q_idx == total_q - 1)
        btn_action = HoverButton(
            btn_bar, text="Submit Answer", font=("Segoe UI", 10, "bold"),
            bg_color=COLOR_ACCENT_TEAL, hover_color=COLOR_TEAL_HOVER, padx=20, pady=8
        )
        btn_action.pack(side="right")

        def handle_action():
            if not self.quiz_answered:
                # STEP A: Validate selection & provide INSTANT FEEDBACK
                chosen = self.selected_choice.get()
                if chosen == -1:
                    messagebox.showwarning("Select Answer", "Please choose an answer option before submitting.")
                    return

                self.quiz_answered = True
                correct_idx = q_data["answer"]
                is_correct = (chosen == correct_idx)

                if is_correct:
                    self.quiz_score += 1
                else:
                    # Save to missed questions for targeted practice
                    if not any(m.get("question") == q_data["question"] for m in student_data.get("missed_questions", [])):
                        student_data["missed_questions"].append(q_data)

                # Log results
                self.quiz_results_log.append({
                    "question": q_data["question"],
                    "options": q_data["options"],
                    "user_choice": chosen,
                    "correct_choice": correct_idx,
                    "is_correct": is_correct,
                    "explanation": q_data.get("explanation", "")
                })

                # Highlight options visually
                for idx, (frame, dot, txt) in enumerate(self.option_cards):
                    if idx == correct_idx:
                        frame.configure(bg=COLOR_TEAL_LIGHT, highlightbackground=COLOR_ACCENT_TEAL, highlightthickness=2)
                        dot.configure(text="✔", fg=COLOR_ACCENT_TEAL, bg=COLOR_TEAL_LIGHT)
                    elif idx == chosen and not is_correct:
                        frame.configure(bg=COLOR_ROSE_LIGHT, highlightbackground=COLOR_ROSE, highlightthickness=2)
                        dot.configure(text="✖", fg=COLOR_ROSE, bg=COLOR_ROSE_LIGHT)

                # Show instant explanation
                feedback_box.configure(bg=COLOR_TEAL_LIGHT if is_correct else COLOR_ROSE_LIGHT, padx=14, pady=10)
                lbl_fb_title.configure(
                    text="✔ Correct Answer!" if is_correct else f"✖ Incorrect. Correct Answer: {q_data['options'][correct_idx]}",
                    fg=COLOR_ACCENT_TEAL if is_correct else COLOR_ROSE,
                    bg=COLOR_TEAL_LIGHT if is_correct else COLOR_ROSE_LIGHT
                )
                lbl_fb_title.pack(anchor="w")

                lbl_fb_expl.configure(
                    text=f"💡 Explanation: {q_data.get('explanation', '')}",
                    bg=COLOR_TEAL_LIGHT if is_correct else COLOR_ROSE_LIGHT
                )
                lbl_fb_expl.pack(anchor="w", pady=(3, 0))

                # Transform button into Next Question
                btn_action.configure(
                    text="View Final Results ➔" if is_last else "Next Question ➔",
                    bg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER
                )
            else:
                # STEP B: Advance to next question or conclude
                self.q_index += 1
                if self.q_index < len(self.active_quiz_questions):
                    self.render_active_question()
                else:
                    self.conclude_quiz()

        btn_action.configure(command=handle_action)

    def conclude_quiz(self):
        """Applies rule-based engine, updates progress, checks achievements, and shows results."""
        total_q = len(self.active_quiz_questions)
        score = self.quiz_score
        student_data = self.get_current_student_data()

        if self.quiz_mode == "missed_practice":
            # For missed practice, evaluate without topic-specific promotion
            pct = round((score / total_q) * 100, 1) if total_q > 0 else 0.0
            eval_res = {
                "percentage": pct,
                "old_level": "Practice",
                "new_level": "Practice",
                "decision": "Practice Session Completed",
                "reason": f"You scored {pct}% on previously missed questions. Consistent practice reinforces long-term retention.",
                "recommended_topic": student_data.get("recommended_next_topic", TOPIC_ORDER[0]),
                "passed": pct >= 80.0
            }
        else:
            t_diff = student_data["topic_progress"].get(self.current_topic, {}).get("level", "Easy")
            eval_res = evaluate_adaptive_performance(
                topic=self.current_topic,
                score=score,
                total_q=total_q,
                current_topic_level=t_diff,
                student_data=student_data
            )

            pct = eval_res["percentage"]
            new_level = eval_res["new_level"]
            rec_topic = eval_res["recommended_topic"]

            # Update topic progress
            student_data["current_difficulty"] = new_level
            student_data["recommended_next_topic"] = rec_topic

            t_stat = student_data["topic_progress"].get(self.current_topic, {})
            t_stat["attempts"] = t_stat.get("attempts", 0) + 1
            t_stat["last_score"] = pct
            t_stat["highest_score"] = max(t_stat.get("highest_score", 0), pct)
            t_stat["level"] = new_level

            if pct >= 80.0:
                t_stat["status"] = "Mastered"
                if self.current_topic not in student_data["completed_topics"]:
                    student_data["completed_topics"].append(self.current_topic)
            elif pct >= 50.0:
                if t_stat["status"] != "Mastered":
                    t_stat["status"] = "In Progress"
            else:
                if t_stat["status"] != "Mastered":
                    t_stat["status"] = "Needs Revision"

            student_data["topic_progress"][self.current_topic] = t_stat

        # Record in history
        student_data["quiz_history"].append({
            "topic": self.current_topic,
            "difficulty": eval_res.get("old_level", "Easy"),
            "score": score,
            "total": total_q,
            "percentage": eval_res["percentage"],
            "promoted_to": eval_res.get("new_level", "Easy"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Check and award badges
        new_badges = check_and_award_achievements(student_data)
        self.save_db()

        if new_badges:
            messagebox.showinfo("Achievement Unlocked!", f"🎉 Congratulations! You unlocked: {', '.join(new_badges)}!")

        self.render_results_screen(eval_res, score, total_q)

    def render_results_screen(self, eval_res, score, total_q):
        """Displays score card, rule decision, and retry / practice options."""
        self.clear_content_area()
        self.update_top_bar(f"Quiz Results / {self.current_topic}")
        self.build_sidebar(active_tab="quiz_start")

        pct = eval_res["percentage"]
        body = self.create_scrollable_container()

        # Score Summary Card
        res_card = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=18, relief="solid", bd=1)
        res_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        res_card.pack(fill="x", pady=(0, 14))

        left_res = tk.Frame(res_card, bg=COLOR_CARD)
        left_res.pack(side="left", fill="x", expand=True)

        tk.Label(
            left_res, text=f"Quiz Complete: {self.current_topic}",
            font=("Segoe UI", 15, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w")

        tk.Label(
            left_res, text=f"Final Score: {score} / {total_q}  ({pct}%)",
            font=("Segoe UI", 13, "bold"), fg=COLOR_SECONDARY, bg=COLOR_CARD
        ).pack(anchor="w", pady=(3, 6))

        if pct >= 80.0:
            badge_bg, badge_fg, badge_txt = COLOR_TEAL_LIGHT, COLOR_ACCENT_TEAL, "🌟 HIGH MASTERY (PROMOTED)"
        elif pct >= 50.0:
            badge_bg, badge_fg, badge_txt = COLOR_AMBER_LIGHT, COLOR_AMBER, "⚡ CONSOLIDATING MASTERY"
        else:
            badge_bg, badge_fg, badge_txt = COLOR_ROSE_LIGHT, COLOR_ROSE, "⚠️ REVISION RECOMMENDED"

        tk.Label(
            left_res, text=badge_txt, font=("Segoe UI", 8, "bold"),
            fg=badge_fg, bg=badge_bg, padx=10, pady=3
        ).pack(anchor="w")

        gauge = CircularGauge(res_card, size=100, thickness=8)
        gauge.pack(side="right", padx=(10, 0))
        gauge_color = COLOR_ACCENT_TEAL if pct >= 80.0 else (COLOR_AMBER if pct >= 50.0 else COLOR_ROSE)
        gauge.set_progress(pct, color=gauge_color, label_text="Score")

        # Adaptive Engine Assessment Card
        adapt_box = tk.Frame(body, bg="#EFF6FF", padx=18, pady=14, relief="solid", bd=1)
        adapt_box.configure(highlightbackground="#BFDBFE", highlightthickness=1)
        adapt_box.pack(fill="x", pady=(0, 14))

        tk.Label(
            adapt_box, text="🤖 Rule-Based Adaptive Learning Assessment",
            font=("Segoe UI", 11, "bold"), fg=COLOR_SECONDARY, bg="#EFF6FF"
        ).pack(anchor="w")

        act_text = f"Action: {eval_res['decision']}  ➔  Target Difficulty: {eval_res['new_level'].upper()}"
        tk.Label(
            adapt_box, text=act_text,
            font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg="#EFF6FF"
        ).pack(anchor="w", pady=(3, 2))

        tk.Label(
            adapt_box, text=eval_res["reason"],
            font=("Segoe UI", 9), fg=COLOR_TEXT_MAIN, bg="#EFF6FF",
            wraplength=830, justify="left"
        ).pack(anchor="w")

        tk.Label(
            adapt_box, text=f"👉 Suggested Next Step: {eval_res['recommended_topic']}",
            font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT_TEAL, bg="#EFF6FF"
        ).pack(anchor="w", pady=(5, 0))

        # Action Buttons Row (Retry, Practice Missed, Return)
        btn_row = tk.Frame(body, bg=COLOR_BG)
        btn_row.pack(fill="x", pady=(0, 16))

        HoverButton(
            btn_row, text="🏠 Dashboard", font=("Segoe UI", 9),
            bg_color=COLOR_CARD, hover_color="#F1F5F9", fg_color=COLOR_TEXT_MAIN,
            padx=14, pady=7, command=self.show_dashboard
        ).pack(side="left", padx=(0, 8))

        if self.quiz_mode == "standard":
            HoverButton(
                btn_row, text="🔁 Retry This Quiz", font=("Segoe UI", 9, "bold"),
                bg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER, padx=14, pady=7,
                command=lambda: self.start_quiz_session(self.current_topic, eval_res["new_level"], mode="standard")
            ).pack(side="left", padx=(0, 8))

        student_data = self.get_current_student_data()
        missed_count = len(student_data.get("missed_questions", []))
        if missed_count > 0:
            HoverButton(
                btn_row, text=f"🎯 Practice Missed ({missed_count})", font=("Segoe UI", 9, "bold"),
                bg_color=COLOR_AMBER, hover_color="#B45309", padx=14, pady=7,
                command=lambda: self.start_quiz_session(None, None, mode="missed_practice")
            ).pack(side="left")

        # Question by Question Review Header
        tk.Label(
            body, text="Detailed Question Analysis & Explanations",
            font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BG
        ).pack(anchor="w", pady=(0, 8))

        for idx, item in enumerate(self.quiz_results_log):
            q_card = tk.Frame(body, bg=COLOR_CARD, padx=16, pady=12, relief="solid", bd=1)
            q_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            q_card.pack(fill="x", pady=3)

            status_sym = "✔ Correct" if item["is_correct"] else "✖ Incorrect"
            status_c = COLOR_ACCENT_TEAL if item["is_correct"] else COLOR_ROSE

            tk.Label(
                q_card, text=f"Q{idx + 1}: {item['question']}  ({status_sym})",
                font=("Segoe UI", 10, "bold"), fg=status_c, bg=COLOR_CARD,
                wraplength=830, justify="left"
            ).pack(anchor="w")

            user_ans = item["options"][item["user_choice"]]
            corr_ans = item["options"][item["correct_choice"]]

            tk.Label(
                q_card, text=f"Your Answer: {user_ans}\nCorrect Answer: {corr_ans}",
                font=("Segoe UI", 9), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, justify="left"
            ).pack(anchor="w", pady=(3, 0))

            if item.get("explanation"):
                tk.Label(
                    q_card, text=f"💡 Why? {item['explanation']}",
                    font=("Segoe UI", 9, "italic"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD,
                    wraplength=830, justify="left"
                ).pack(anchor="w", pady=(3, 0))

    # =======================================================================
    # SCREEN 6: BOOKMARKED QUESTIONS MANAGEMENT
    # =======================================================================
    def show_bookmarks(self):
        """Displays student's saved difficult questions with answers & explanations."""
        self.clear_content_area()
        self.update_top_bar("Bookmarks / Saved Questions")
        self.build_sidebar(active_tab="bookmarks")

        student_data = self.get_current_student_data()
        bookmarks = student_data.get("bookmarks", [])
        body = self.create_scrollable_container()

        hdr = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=16, relief="solid", bd=1)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 16))

        tk.Label(
            hdr, text=f"⭐ Bookmarked Questions ({len(bookmarks)})",
            font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Review difficult questions saved during quizzes. Bookmarking enables targeted spaced repetition.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
        ).pack(anchor="w", pady=(2, 0))

        if not bookmarks:
            empty_box = tk.Frame(body, bg=COLOR_CARD, padx=30, pady=40, relief="solid", bd=1)
            empty_box.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            empty_box.pack(fill="x")

            tk.Label(
                empty_box, text="No Bookmarked Questions Yet!",
                font=("Segoe UI", 14, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
            ).pack()

            tk.Label(
                empty_box,
                text="While taking any adaptive quiz, click the '☆ Bookmark Question' button\nto save challenging questions here for revision anytime.",
                font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, justify="center"
            ).pack(pady=(6, 16))

            HoverButton(
                empty_box, text="Go to Adaptive Quiz ➔", font=("Segoe UI", 9, "bold"),
                bg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER, padx=16, pady=7,
                command=lambda: self.show_quiz_launcher(None)
            ).pack()
            return

        for idx, item in enumerate(bookmarks):
            card = tk.Frame(body, bg=COLOR_CARD, padx=18, pady=14, relief="solid", bd=1)
            card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            card.pack(fill="x", pady=4)

            # Header row
            h_row = tk.Frame(card, bg=COLOR_CARD)
            h_row.pack(fill="x", pady=(0, 4))

            tk.Label(
                h_row, text=f"Question #{idx + 1}  •  Topic: {item.get('topic', 'General')} ({item.get('difficulty', 'Medium')} Level)",
                font=("Segoe UI", 9, "bold"), fg=COLOR_SECONDARY, bg=COLOR_CARD
            ).pack(side="left")

            def remove_bm(q_text=item["question"]):
                student_data["bookmarks"] = [b for b in student_data["bookmarks"] if b.get("question") != q_text]
                self.save_db()
                self.show_bookmarks()

            btn_del = tk.Button(
                h_row, text="Remove ✕", font=("Segoe UI", 8, "bold"),
                fg=COLOR_ROSE, bg=COLOR_CARD, bd=0, cursor="hand2",
                command=remove_bm
            )
            btn_del.pack(side="right")

            tk.Label(
                card, text=item["question"], font=("Segoe UI", 11, "bold"),
                fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, wraplength=830, justify="left"
            ).pack(anchor="w")

            # Correct answer & options
            corr_idx = item.get("answer", 0)
            corr_text = item["options"][corr_idx] if corr_idx < len(item["options"]) else "N/A"

            ans_box = tk.Frame(card, bg=COLOR_TEAL_LIGHT, padx=10, pady=6)
            ans_box.pack(fill="x", pady=(6, 4))

            tk.Label(
                ans_box, text=f"✔ Correct Answer: {corr_text}",
                font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT_TEAL, bg=COLOR_TEAL_LIGHT
            ).pack(anchor="w")

            if item.get("explanation"):
                tk.Label(
                    card, text=f"💡 Explanation: {item['explanation']}",
                    font=("Segoe UI", 9, "italic"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD,
                    wraplength=830, justify="left"
                ).pack(anchor="w")

    # =======================================================================
    # SCREEN 7: ACHIEVEMENTS & REWARDS SYSTEM
    # =======================================================================
    def show_achievements(self):
        """Displays unlocked badges and learning streak milestones."""
        self.clear_content_area()
        self.update_top_bar("Achievements & Badges")
        self.build_sidebar(active_tab="achievements")

        student_data = self.get_current_student_data()
        unlocked_set = set(student_data.get("achievements", []))
        body = self.create_scrollable_container()

        hdr = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=16, relief="solid", bd=1)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 16))

        tk.Label(
            hdr, text=f"🏆 Learning Achievements ({len(unlocked_set)} / {len(ACHIEVEMENT_DEFINITIONS)})",
            font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Milestone rewards earned through quizzes, topic masteries, and active practice.",
            font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
        ).pack(anchor="w", pady=(2, 0))

        # Achievements Grid
        for ach in ACHIEVEMENT_DEFINITIONS:
            is_unlocked = ach["id"] in unlocked_set
            card = tk.Frame(body, bg=COLOR_CARD, padx=18, pady=14, relief="solid", bd=1)
            card.configure(
                highlightbackground=COLOR_ACCENT_TEAL if is_unlocked else COLOR_BORDER,
                highlightthickness=2 if is_unlocked else 1
            )
            card.pack(fill="x", pady=4)

            # Left Icon
            lbl_icon = tk.Label(
                card, text=ach["icon"], font=("Segoe UI", 22),
                bg=COLOR_CARD
            )
            lbl_icon.pack(side="left", padx=(0, 14))

            # Info
            f_txt = tk.Frame(card, bg=COLOR_CARD)
            f_txt.pack(side="left", fill="x", expand=True)

            tk.Label(
                f_txt, text=ach["title"], font=("Segoe UI", 11, "bold"),
                fg=COLOR_TEXT_MAIN if is_unlocked else COLOR_TEXT_MUTED, bg=COLOR_CARD
            ).pack(anchor="w")

            tk.Label(
                f_txt, text=ach["desc"], font=("Segoe UI", 9),
                fg=COLOR_TEXT_MUTED, bg=COLOR_CARD
            ).pack(anchor="w")

            # Status Badge
            if is_unlocked:
                status_lbl = tk.Label(
                    card, text="UNLOCKED 🌟", font=("Segoe UI", 8, "bold"),
                    fg=COLOR_ACCENT_TEAL, bg=COLOR_TEAL_LIGHT, padx=10, pady=4
                )
            else:
                status_lbl = tk.Label(
                    card, text="LOCKED 🔒", font=("Segoe UI", 8, "bold"),
                    fg="#94A3B8", bg="#F1F5F9", padx=10, pady=4
                )
            status_lbl.pack(side="right")

    # =======================================================================
    # SCREEN 8: LEARNING PROGRESS & ADVANCED ANALYTICS
    # =======================================================================
    def show_progress_analytics(self):
        """Displays topic performance, strongest & weakest topics, and Canvas bar chart."""
        self.clear_content_area()
        self.update_top_bar("Progress & Analytics")
        self.build_sidebar(active_tab="analytics")

        student_data = self.get_current_student_data()
        student_name = self.active_student
        current_diff = student_data.get("current_difficulty", "Easy")
        completed = student_data.get("completed_topics", [])
        quiz_hist = student_data.get("quiz_history", [])

        body = self.create_scrollable_container()

        hdr = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=16, relief="solid", bd=1)
        hdr.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 16))

        tk.Label(
            hdr, text=f"Performance Analytics: {student_name}",
            font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(side="left")

        diff_badge = tk.Label(
            hdr, text=f"CURRENT DIFFICULTY: {current_diff.upper()}",
            font=("Segoe UI", 8, "bold"), fg="#FFFFFF", bg=COLOR_SECONDARY,
            padx=10, pady=4
        )
        diff_badge.pack(side="right")

        # Determine Strongest & Focus Area (Needs Improvement) Topics
        topic_scores = {t: student_data["topic_progress"].get(t, {}).get("highest_score", 0) for t in TOPIC_ORDER}
        strongest_topic = max(topic_scores, key=topic_scores.get)
        weakest_topic = min(topic_scores, key=topic_scores.get)

        # Strengths & Weaknesses Cards Row
        diag_row = tk.Frame(body, bg=COLOR_BG)
        diag_row.pack(fill="x", pady=(0, 14))

        # Strongest Card
        c_str = tk.Frame(diag_row, bg=COLOR_CARD, padx=16, pady=12, relief="solid", bd=1)
        c_str.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        c_str.pack(side="left", fill="both", expand=True, padx=(0, 4))

        tk.Label(c_str, text="🌟 STRONGEST TOPIC", font=("Segoe UI", 8, "bold"), fg=COLOR_ACCENT_TEAL, bg=COLOR_CARD).pack(anchor="w")
        tk.Label(c_str, text=f"{strongest_topic} ({int(topic_scores[strongest_topic])}%)", font=("Segoe UI", 13, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD).pack(anchor="w", pady=(2, 0))

        # Focus Area Card
        c_weak = tk.Frame(diag_row, bg=COLOR_CARD, padx=16, pady=12, relief="solid", bd=1)
        c_weak.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        c_weak.pack(side="right", fill="both", expand=True, padx=(4, 0))

        tk.Label(c_weak, text="⚠️ NEEDS IMPROVEMENT", font=("Segoe UI", 8, "bold"), fg=COLOR_ROSE, bg=COLOR_CARD).pack(anchor="w")
        tk.Label(c_weak, text=f"{weakest_topic} ({int(topic_scores[weakest_topic])}%)", font=("Segoe UI", 13, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD).pack(anchor="w", pady=(2, 0))

        # Visual Performance Canvas Bar Chart
        chart_card = tk.Frame(body, bg=COLOR_CARD, padx=20, pady=16, relief="solid", bd=1)
        chart_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        chart_card.pack(fill="x", pady=(0, 16))

        tk.Label(
            chart_card, text=f"📊 Topic Mastery Comparison (Highest Quiz Score %)",
            font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w", pady=(0, 10))

        chart_canvas = tk.Canvas(chart_card, width=820, height=180, bg="#F8FAFC", highlightthickness=0)
        chart_canvas.pack(fill="x")

        # Gridlines & 80% Mastery guideline
        chart_canvas.create_line(50, 15, 50, 145, fill="#CBD5E1", width=2)
        chart_canvas.create_line(50, 145, 800, 145, fill="#CBD5E1", width=2)

        # 80% Mastery Line (Green dotted reference)
        y_80 = 145 - (80 * 1.25)
        chart_canvas.create_line(50, y_80, 800, y_80, fill="#A7F3D0", width=1, dash=(4, 2))
        chart_canvas.create_text(750, y_80 - 8, text="80% Mastery Goal", font=("Segoe UI", 7, "bold"), fill=COLOR_ACCENT_TEAL)

        for y_val in [0, 25, 50, 75, 100]:
            y_pos = 145 - (y_val * 1.25)
            chart_canvas.create_text(30, y_pos, text=f"{y_val}%", font=("Segoe UI", 8), fill=COLOR_TEXT_MUTED)
            chart_canvas.create_line(46, y_pos, 800, y_pos, fill="#F1F5F9", width=1)

        bar_width = 75
        gap = 70
        start_x = 75

        for idx, t in enumerate(TOPIC_ORDER):
            t_score = topic_scores[t]
            x1 = start_x + (idx * (bar_width + gap))
            x2 = x1 + bar_width
            bar_height = t_score * 1.25
            y1 = 145 - bar_height
            y2 = 145

            bar_color = COLOR_ACCENT_TEAL if t_score >= 80.0 else (COLOR_AMBER if t_score >= 50.0 else (COLOR_SECONDARY if t_score > 0 else "#CBD5E1"))

            chart_canvas.create_rectangle(x1, y1, x2, y2, fill=bar_color, outline="")
            chart_canvas.create_text(x1 + (bar_width / 2), y1 - 8, text=f"{int(t_score)}%", font=("Segoe UI", 8, "bold"), fill=COLOR_TEXT_MAIN)
            short_t = t if len(t) < 13 else t[:11] + ".."
            chart_canvas.create_text(x1 + (bar_width / 2), 160, text=short_t, font=("Segoe UI", 8), fill=COLOR_TEXT_MUTED)

        # Topic Breakdown Table Card
        tb_card = tk.Frame(body, bg=COLOR_CARD, padx=20, pady=16, relief="solid", bd=1)
        tb_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        tb_card.pack(fill="x", pady=(0, 16))

        tk.Label(tb_card, text="📋 Curriculum Topics Detail Breakdown", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD).pack(anchor="w", pady=(0, 8))

        for t in TOPIC_ORDER:
            t_data = student_data["topic_progress"].get(t, {})
            row = tk.Frame(tb_card, bg=COLOR_CARD, pady=4)
            row.pack(fill="x")

            tk.Label(row, text=t, font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, width=22, anchor="w").pack(side="left")
            tk.Label(row, text=f"Level: {t_data.get('level', 'Easy')}", font=("Segoe UI", 9), fg=COLOR_SECONDARY, bg=COLOR_CARD, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=f"Attempts: {t_data.get('attempts', 0)}", font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=f"Best: {t_data.get('highest_score', 0)}%", font=("Segoe UI", 9, "bold"), fg=COLOR_ACCENT_TEAL, bg=COLOR_CARD, width=14, anchor="w").pack(side="left")
            tk.Label(row, text=f"Status: {t_data.get('status', 'Not Started')}", font=("Segoe UI", 9), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD).pack(side="left")

        # Action Buttons (Export Report Card, Reset Progress)
        act_row = tk.Frame(body, bg=COLOR_BG)
        act_row.pack(fill="x", pady=10)

        HoverButton(
            act_row, text="📄 Export Progress Report (.txt)", font=("Segoe UI", 9, "bold"),
            bg_color=COLOR_ACCENT_TEAL, hover_color=COLOR_TEAL_HOVER, padx=16, pady=7,
            command=self.export_report
        ).pack(side="left")

        def reset_progress():
            if messagebox.askyesno("Reset Student Record", f"Are you sure you want to reset all quiz progress and achievements for '{student_name}'?"):
                self.db["students"][student_name] = create_empty_student_profile()
                self.save_db()
                self.show_progress_analytics()

        HoverButton(
            act_row, text=f"🗑 Reset Progress for {student_name}", font=("Segoe UI", 9),
            bg_color=COLOR_ROSE_LIGHT, hover_color="#FECDD3", fg_color=COLOR_ROSE,
            padx=14, pady=7, command=reset_progress
        ).pack(side="right")

    # =======================================================================
    # SCREEN 9: ABOUT SDG 4 (QUALITY EDUCATION)
    # =======================================================================
    def show_sdg4(self):
        """Displays explanation of UN Sustainable Development Goal 4 integration."""
        self.clear_content_area()
        self.update_top_bar("UN SDG 4: Quality Education")
        self.build_sidebar(active_tab="sdg4")

        body = self.create_scrollable_container()

        # Official Red SDG 4 Banner Card
        banner = tk.Frame(body, bg="#C5192D", padx=24, pady=18, relief="flat")
        banner.pack(fill="x", pady=(0, 16))

        tk.Label(
            banner, text="UNITED NATIONS SUSTAINABLE DEVELOPMENT GOAL 4",
            font=("Segoe UI", 9, "bold"), fg="#FECDD3", bg="#C5192D"
        ).pack(anchor="w")

        tk.Label(
            banner, text="Quality Education for Everyone",
            font=("Segoe UI", 18, "bold"), fg="#FFFFFF", bg="#C5192D"
        ).pack(anchor="w", pady=(2, 4))

        tk.Label(
            banner,
            text="\"Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all.\"",
            font=("Segoe UI", 10, "italic"), fg="#FFE4E6", bg="#C5192D",
            wraplength=830, justify="left"
        ).pack(anchor="w")

        # Core Alignment Pillars Card
        pillars_card = tk.Frame(body, bg=COLOR_CARD, padx=22, pady=18, relief="solid", bd=1)
        pillars_card.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        pillars_card.pack(fill="x", pady=(0, 16))

        tk.Label(
            pillars_card, text="How this Adaptive Learning Platform directly implements SDG 4:",
            font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD
        ).pack(anchor="w", pady=(0, 10))

        pillars = [
            (
                "1. Personalized & Adaptive Pacing (Cognitive Fit)",
                "Traditional classrooms enforce one rigid teaching pace, leaving struggling students behind and under-stimulating advanced learners. This platform's rule engine automatically modulates quiz difficulty according to personal scores, ensuring every student learns at their optimal cognitive challenge."
            ),
            (
                "2. Equitable, Zero-Cost & Offline-Ready Accessibility",
                "Built using standard Python, local JSON storage, and a native desktop UI, the application runs 100% offline without requiring high-end GPUs, internet bandwidth, or costly API subscriptions. This enables deployment in underserved rural schools and resource-constrained environments."
            ),
            (
                "3. Immediate Formative Feedback & Misconception Prevention",
                "Rather than merely displaying an arbitrary final score, the platform delivers clear conceptual explanations immediately following each quiz question. This prevents misconceptions from solidifying and empowers students to self-correct in real time."
            ),
            (
                "4. Identifying Individual Knowledge Gaps",
                "By tracking progress and difficulty on a topic-by-topic basis (rather than a global score), the system identifies specific topics where a student struggles (e.g. Loops vs Functions) and recommends targeted revision."
            ),
            (
                "5. Fostering Foundational Digital Literacy",
                "Programming fundamentals are essential competencies for modern lifelong careers. By guiding students through variables, logic, loops, and functions with interactive code execution, the platform actively bridges the digital divide."
            )
        ]

        for title, text in pillars:
            p_box = tk.Frame(pillars_card, bg=COLOR_CARD, pady=6)
            p_box.pack(fill="x", anchor="w")

            tk.Label(
                p_box, text=title, font=("Segoe UI", 10, "bold"),
                fg=COLOR_SECONDARY, bg=COLOR_CARD
            ).pack(anchor="w")

            tk.Label(
                p_box, text=text, font=("Segoe UI", 9),
                fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, wraplength=830, justify="left"
            ).pack(anchor="w", pady=(2, 0))

        HoverButton(
            body, text="⬅ Back to Dashboard", font=("Segoe UI", 9, "bold"),
            bg_color=COLOR_CARD, hover_color="#F1F5F9", fg_color=COLOR_TEXT_MAIN,
            padx=16, pady=7, command=self.show_dashboard
        ).pack(anchor="w")

    # =======================================================================
    # FEATURE: EXPORT PRINTABLE LEARNING REPORT
    # =======================================================================
    def export_report(self):
        """Generates a clean text/markdown learning report card file."""
        student_data = self.get_current_student_data()
        student_name = self.active_student
        current_diff = student_data.get("current_difficulty", "Easy")
        completed = student_data.get("completed_topics", [])
        quiz_hist = student_data.get("quiz_history", [])

        report_filename = f"Learning_Report_{student_name.replace(' ', '_')}.txt"
        save_path = os.path.join(BASE_DIR, report_filename)

        lines = [
            "================================================================================",
            "          ADAPTIVE LEARNING PLATFORM - STUDENT PROGRESS REPORT",
            "                    Aligned with UN SDG 4: Quality Education",
            "================================================================================",
            f"Student Name            : {student_name}",
            f"Report Generated On     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Current Adaptive Level  : {current_diff.upper()}",
            f"Curriculum Topics Done  : {len(completed)} of {len(TOPIC_ORDER)} Completed",
            "--------------------------------------------------------------------------------",
            "TOPIC BREAKDOWN:",
            "--------------------------------------------------------------------------------"
        ]

        for t in TOPIC_ORDER:
            t_data = student_data["topic_progress"].get(t, {})
            status = t_data.get("status", "Not Started")
            attempts = t_data.get("attempts", 0)
            high_s = t_data.get("highest_score", 0)
            t_lvl = t_data.get("level", "Easy")
            lines.append(f"  • {t:<22} | Level: {t_lvl:<6} | Status: {status:<12} | Attempts: {attempts:<2} | Best: {high_s}%")

        lines.extend([
            "--------------------------------------------------------------------------------",
            "RECENT QUIZ ATTEMPTS (LAST 5):",
            "--------------------------------------------------------------------------------"
        ])

        if not quiz_hist:
            lines.append("  No quiz attempts recorded yet.")
        else:
            for h in quiz_hist[-5:]:
                lines.append(f"  [{h.get('timestamp')}] {h.get('topic'):<15} ({h.get('difficulty')} Level) -> Score: {h.get('score')}/{h.get('total')} ({h.get('percentage')}%)")

        lines.extend([
            "================================================================================",
            "                   UNITED NATIONS SDG 4 : QUALITY EDUCATION",
            "   Ensuring inclusive and equitable quality education and promoting lifelong",
            "                      learning opportunities for all.",
            "================================================================================"
        ])

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Report Exported", f"Student progress report successfully exported to:\n\n{save_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save report: {e}")


# ===========================================================================
# APPLICATION ENTRY POINT
# ===========================================================================
if __name__ == "__main__":
    app = AdaptiveLearningApp()
    app.mainloop()
