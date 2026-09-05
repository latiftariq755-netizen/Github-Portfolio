"""
UET University — ECAT Exam Portal
===================================
Combined project: Login System (PyQt5 + SQLite) + ECAT Exam Engine

Dependencies:
    pip install PyQt5

Run:
    python uet_ecat_portal.py

Default credentials (seeded on first run):
    Student  →  ID: STU001   Password: student123
    Admin    →  ID: ADM001   Password: admin123
"""

import sys
import sqlite3
import hashlib
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QLabel,
    QPushButton, QLineEdit, QTabWidget, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QButtonGroup,
    QRadioButton, QScrollArea, QProgressBar, QSizePolicy,
    QInputDialog, QStackedWidget, QTextEdit, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QColor

# ══════════════════════════════════════════════════════════
#  DATABASE LAYER
# ══════════════════════════════════════════════════════════

DB_PATH = "uet_ecat.db"


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id  TEXT UNIQUE NOT NULL,
        full_name   TEXT NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        department  TEXT NOT NULL,
        semester    INTEGER NOT NULL DEFAULT 1,
        password    TEXT NOT NULL,
        created_at  TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS admins (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id    TEXT UNIQUE NOT NULL,
        full_name   TEXT NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        role        TEXT NOT NULL DEFAULT 'Admin',
        password    TEXT NOT NULL,
        created_at  TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        subject     TEXT NOT NULL,
        question    TEXT NOT NULL,
        option_a    TEXT NOT NULL,
        option_b    TEXT NOT NULL,
        option_c    TEXT NOT NULL,
        option_d    TEXT NOT NULL,
        answer      TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS exam_results (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id      TEXT NOT NULL,
        student_name    TEXT NOT NULL,
        score           INTEGER NOT NULL,
        correct         INTEGER NOT NULL,
        wrong           INTEGER NOT NULL,
        skipped         INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        percentage      REAL NOT NULL,
        grade           TEXT NOT NULL,
        exam_date       TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS result_details (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        result_id       INTEGER NOT NULL,
        question_text   TEXT NOT NULL,
        student_answer  TEXT NOT NULL,
        correct_answer  TEXT NOT NULL,
        status          TEXT NOT NULL,
        FOREIGN KEY(result_id) REFERENCES exam_results(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS login_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT NOT NULL,
        user_type   TEXT NOT NULL,
        status      TEXT NOT NULL,
        timestamp   TEXT NOT NULL
    )""")

    # ── Seed default data ──────────────────────────────
    now = datetime.now().isoformat(sep=" ", timespec="seconds")

    if c.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        c.executemany("""INSERT INTO students
            (student_id,full_name,email,department,semester,password,created_at)
            VALUES (?,?,?,?,?,?,?)""", [
            ("student", "Latif Tariq",    "latif@uet.edu.pk",  "Computer Engineering",      4, hash_password("student123"), now),
            
        ])

    if c.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
        c.execute("""INSERT INTO admins
            (admin_id,full_name,email,role,password,created_at)
            VALUES (?,?,?,?,?,?)""",
            ("ecat_admin","Dr. Latif Tariq","admin@uet.edu.pk","Super Admin",hash_password("ecat@2026"),now))

    if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        seed_questions = [
            ("Computer",     "Which one is the fastest memory?",                  "RAM",       "CPU",      "Cache",        "Hard Drive",     "C"),
            ("Mathematics",  "What is the value of (5+3)*3?",                     "8",         "10",       "24",           "13",             "C"),
            ("Physics",      "What is the SI unit of acceleration?",              "m/s^3",     "m/s^2",    "km/h",         "m/s",            "B"),
            ("Mathematics",  "What is the formula of Volume?",                    "A * W",     "L * W * H","A ^ 2",        "L ^ 2",          "B"),
            ("English",      "Choose the correct synonym of 'Intricate'.",        "Simple",    "Complex",  "Straightforward","Easy",          "B"),
            ("Mathematics",  "What is the derivative of x^2?",                   "x",         "2x",       "x^2",          "2",              "B"),
            ("Physics",      "What is the speed of light in vacuum?",             "3x10^4 m/s","3x10^6 m/s","3x10^8 m/s", "None of above",  "C"),
            ("English",      "Which is the antonym of 'Abundant'?",              "Plentiful", "Scarce",   "Ample",        "Copious",        "B"),
            ("Computer",     "Which of the following is a programming language?", "SQL",       "Python",   "HTML",         "CSS",            "B"),
            ("English",      "Choose the correct antonym of 'Ancient'.",          "Old",       "Modern",   "Past",         "Historic",       "B"),
        ]
        c.executemany("""INSERT INTO questions
            (subject,question,option_a,option_b,option_c,option_d,answer)
            VALUES (?,?,?,?,?,?,?)""", seed_questions)

    conn.commit()
    conn.close()


# ── Auth helpers ────────────────────────────────────────
def auth_student(sid, pw):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM students WHERE student_id=? AND password=?",
        (sid, hash_password(pw))
    ).fetchone()
    conn.close()
    return row

def auth_admin(aid, pw):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM admins WHERE admin_id=? AND password=?",
        (aid, hash_password(pw))
    ).fetchone()
    conn.close()
    return row

def log_login(uid, utype, status):
    conn = get_conn()
    conn.execute(
        "INSERT INTO login_logs (user_id,user_type,status,timestamp) VALUES (?,?,?,?)",
        (uid, utype, status, datetime.now().isoformat(sep=" ", timespec="seconds"))
    )
    conn.commit(); conn.close()

def reset_password(uid, utype, new_pw):
    conn = get_conn()
    table = "students" if utype == "student" else "admins"
    col   = "student_id" if utype == "student" else "admin_id"
    cur = conn.execute(f"UPDATE {table} SET password=? WHERE {col}=?",
                       (hash_password(new_pw), uid))
    ok = cur.rowcount > 0
    conn.commit(); conn.close()
    return ok

# ── Question helpers ─────────────────────────────────────
def get_questions():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM questions").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_question_db(subject, question, a, b, c, d, answer):
    try:
        conn = get_conn()
        conn.execute("""INSERT INTO questions
            (subject,question,option_a,option_b,option_c,option_d,answer)
            VALUES (?,?,?,?,?,?,?)""", (subject, question, a, b, c, d, answer))
        conn.commit(); conn.close()
        return True, "Question added."
    except Exception as e:
        return False, str(e)

def update_question_db(qid, subject, question, a, b, c, d, answer):
    conn = get_conn()
    conn.execute("""UPDATE questions SET subject=?,question=?,option_a=?,
        option_b=?,option_c=?,option_d=?,answer=? WHERE id=?""",
        (subject, question, a, b, c, d, answer, qid))
    conn.commit(); conn.close()

def delete_question_db(qid):
    conn = get_conn()
    conn.execute("DELETE FROM questions WHERE id=?", (qid,))
    conn.commit(); conn.close()

# ── Result helpers ───────────────────────────────────────
def save_result(student_id, student_name, score, correct, wrong,
                skipped, total, percentage, grade, details):
    conn = get_conn()
    cur = conn.execute("""INSERT INTO exam_results
        (student_id,student_name,score,correct,wrong,skipped,
         total_questions,percentage,grade,exam_date)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (student_id, student_name, score, correct, wrong, skipped, total,
         percentage, grade, datetime.now().strftime("%d-%m-%Y %I:%M %p")))
    result_id = cur.lastrowid
    for d in details:
        conn.execute("""INSERT INTO result_details
            (result_id,question_text,student_answer,correct_answer,status)
            VALUES (?,?,?,?,?)""",
            (result_id, d["question"], d["student_answer"],
             d["correct_answer"], d["status"]))
    conn.commit(); conn.close()
    return result_id

def get_all_results():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM exam_results ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_result_details(result_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM result_details WHERE result_id=?", (result_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_results(student_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM exam_results WHERE student_id=? ORDER BY id DESC",
        (student_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_students():
    conn = get_conn()
    rows = conn.execute(
        "SELECT student_id,full_name,email,department,semester,created_at FROM students"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_student_db(sid, name, email, dept, sem, pw):
    try:
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        conn = get_conn()
        conn.execute("""INSERT INTO students
            (student_id,full_name,email,department,semester,password,created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (sid, name, email, dept, sem, hash_password(pw), now))
        conn.commit(); conn.close()
        return True, "Student added."
    except sqlite3.IntegrityError as e:
        return False, str(e)

def calculate_grade(pct):
    if pct >= 80: return "EXCELLENT"
    elif pct >= 65: return "GOOD"
    elif pct >= 50: return "AVERAGE"
    else: return "BELOW AVERAGE"


# ══════════════════════════════════════════════════════════
#  STYLE CONSTANTS
# ══════════════════════════════════════════════════════════

BLUE      = "#1565C0"
BLUE_D    = "#0d47a1"
GREEN     = "#2e7d32"
RED       = "#c62828"
ORANGE    = "#e65100"
PURPLE    = "#6a1b9a"
BG        = "#f4f6fb"
WHITE     = "#ffffff"
GREY      = "#888888"
BORDER    = "#dde1ea"

LOGIN_STYLE = """
QDialog, QWidget { background:#ffffff; font-family:"Segoe UI",Arial,sans-serif; }
QLabel#lblUniversityName { font-size:22px; font-weight:bold; color:#1a1a2e; }
QLabel#lblPortalSub { font-size:13px; color:#888; }
QTabWidget::pane { border:none; background:transparent; }
QTabBar::tab {
    background:transparent; color:#aaa; font-size:12px; font-weight:bold;
    letter-spacing:.8px; padding:10px 20px; min-width:140px;
    border:none; border-bottom:2px solid transparent;
}
QTabBar::tab:selected { color:#1565C0; border-bottom:2px solid #1565C0; }
QLineEdit {
    background:#fafbff; border:1.5px solid #dde1ea; border-radius:10px;
    padding:12px 14px; font-size:14px; color:#222; min-height:20px;
}
QLineEdit:focus { border-color:#1565C0; background:#fff; }
QPushButton#btnLoginStudent, QPushButton#btnLoginAdmin {
    background:#1565C0; color:#fff; border:none; border-radius:10px;
    padding:14px; font-size:13px; font-weight:bold; letter-spacing:1.2px;
}
QPushButton#btnLoginStudent:hover, QPushButton#btnLoginAdmin:hover { background:#0d47a1; }
QPushButton#btnLoginStudent:pressed, QPushButton#btnLoginAdmin:pressed { background:#0a3880; }
QPushButton#btnForgotPassword, QPushButton#btnForgotPasswordAdmin {
    background:transparent; border:none; color:#1565C0; font-size:13px;
}
QPushButton#btnForgotPassword:hover, QPushButton#btnForgotPasswordAdmin:hover { color:#0d47a1; }
QPushButton#btnClose {
    background:transparent; border:1.5px solid #ccc; border-radius:16px;
    color:#555; font-size:14px; font-weight:bold;
    min-width:32px; max-width:32px; min-height:32px; max-height:32px;
}
QPushButton#btnClose:hover { background:#f0f0f0; color:#111; }
"""

DASH_STYLE = """
QMainWindow, QWidget { background:#f4f6fb; font-family:"Segoe UI",Arial,sans-serif; }
QLabel { color:#1a1a2e; }
QPushButton { border-radius:8px; padding:8px 18px; font-size:13px; font-weight:bold; }
QPushButton#btnPrimary   { background:#1565C0; color:white; border:none; }
QPushButton#btnPrimary:hover { background:#0d47a1; }
QPushButton#btnDanger    { background:#e53935; color:white; border:none; }
QPushButton#btnDanger:hover  { background:#b71c1c; }
QPushButton#btnSecondary { background:white; color:#1565C0; border:1.5px solid #1565C0; }
QPushButton#btnSecondary:hover { background:#e3eefe; }
QPushButton#btnSuccess   { background:#2e7d32; color:white; border:none; }
QPushButton#btnSuccess:hover { background:#1b5e20; }
QPushButton#btnWarning   { background:#e65100; color:white; border:none; }
QPushButton#btnWarning:hover { background:#bf360c; }
QTableWidget {
    background:white; border:1px solid #dde1ea; border-radius:10px;
    gridline-color:#f0f2f8; font-size:13px;
}
QTableWidget::item { padding:8px; }
QTableWidget::item:selected { background:#e3eefe; color:#1565C0; }
QHeaderView::section {
    background:#f4f6fb; color:#888; font-size:11px; font-weight:bold;
    letter-spacing:.5px; padding:8px 10px; border:none; border-bottom:1px solid #dde1ea;
}
QFrame#card { background:white; border-radius:14px; border:1px solid #dde1ea; }
QScrollArea { border:none; background:transparent; }
QRadioButton { font-size:14px; color:#1a1a2e; padding:4px 0; spacing:10px; }
QRadioButton::indicator { width:18px; height:18px; }
QRadioButton::indicator:unchecked {
    border:2px solid #bbb; border-radius:9px; background:white;
}
QRadioButton::indicator:checked {
    border:2px solid #1565C0; border-radius:9px; background:#1565C0;
}
QProgressBar {
    border:none; background:#e0e7f7; border-radius:6px;
    text-align:center; font-size:12px; font-weight:bold; color:#1565C0;
    min-height:12px;
}
QProgressBar::chunk { background:#1565C0; border-radius:6px; }
"""

EXAM_TIMER_STYLE_NORMAL  = "font-size:20px; font-weight:bold; color:#1565C0;"
EXAM_TIMER_STYLE_WARNING = "font-size:20px; font-weight:bold; color:#e65100;"
EXAM_TIMER_STYLE_DANGER  = "font-size:20px; font-weight:bold; color:#c62828;"


# ══════════════════════════════════════════════════════════
#  SHARED WIDGETS
# ══════════════════════════════════════════════════════════

class StatCard(QFrame):
    def __init__(self, title, value, color=BLUE, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedHeight(90)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet(f"font-size:12px; color:{GREY}; font-weight:bold; letter-spacing:.5px;")
        v = QLabel(str(value))
        v.setStyleSheet(f"font-size:26px; font-weight:bold; color:{color};")
        lay.addWidget(t); lay.addWidget(v)


def make_table(headers):
    t = QTableWidget()
    t.setColumnCount(len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QTableWidget.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectRows)
    t.verticalHeader().setVisible(False)
    t.horizontalHeader().setStretchLastSection(True)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    return t


def fill_table(table, rows, keys, transforms=None):
    table.setRowCount(len(rows))
    for ri, row in enumerate(rows):
        for ci, key in enumerate(keys):
            val = str(row[key]) if not (transforms and key in transforms) else transforms[key](row[key])
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(ri, ci, item)


# ══════════════════════════════════════════════════════════
#  EXAM WINDOW
# ══════════════════════════════════════════════════════════

EXAM_DURATION_SECONDS = 20 * 60   # 20 minutes

class ExamWindow(QMainWindow):
    def __init__(self, student_data, parent_dashboard=None):
        super().__init__()
        self.student    = student_data
        self.parent_db  = parent_dashboard
        self.questions  = get_questions()
        self.current_q  = 0
        self.answers    = {}          # index → "A"/"B"/"C"/"D"/"S"
        self.time_left  = EXAM_DURATION_SECONDS
        self.submitted  = False

        self.setWindowTitle("UET ECAT Exam")
        self.setMinimumSize(780, 580)
        self.setStyleSheet(DASH_STYLE)
        self._build_ui()
        self._load_question(0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    # ── UI ─────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        lbl_title = QLabel("📝  ECAT Examination")
        lbl_title.setStyleSheet("font-size:18px; font-weight:bold;")

        self.lbl_timer = QLabel("20:00")
        self.lbl_timer.setStyleSheet(EXAM_TIMER_STYLE_NORMAL)

        self.lbl_student = QLabel(
            f"{self.student['full_name']}  ·  {self.student['student_id']}"
        )
        self.lbl_student.setStyleSheet(f"font-size:13px; color:{GREY};")

        hdr.addWidget(lbl_title)
        hdr.addStretch()
        hdr.addWidget(self.lbl_student)
        hdr.addSpacing(20)
        hdr.addWidget(self.lbl_timer)
        root.addLayout(hdr)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(len(self.questions))
        self.progress.setValue(1)
        root.addWidget(self.progress)

        # Question card
        self.q_card = QFrame()
        self.q_card.setObjectName("card")
        q_lay = QVBoxLayout(self.q_card)
        q_lay.setContentsMargins(24, 20, 24, 20)
        q_lay.setSpacing(14)

        self.lbl_qnum = QLabel()
        self.lbl_qnum.setStyleSheet(f"font-size:12px; color:{GREY}; font-weight:bold;")

        self.lbl_subject = QLabel()
        self.lbl_subject.setStyleSheet(f"font-size:12px; color:{BLUE}; font-weight:bold;")

        self.lbl_question = QLabel()
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setStyleSheet("font-size:16px; font-weight:bold; color:#1a1a2e;")

        top_row = QHBoxLayout()
        top_row.addWidget(self.lbl_qnum)
        top_row.addStretch()
        top_row.addWidget(self.lbl_subject)

        q_lay.addLayout(top_row)
        q_lay.addWidget(self.lbl_question)

        # Options
        self.btn_group = QButtonGroup(self)
        self.option_btns = []
        for opt in ["A", "B", "C", "D"]:
            rb = QRadioButton()
            rb.setProperty("opt_key", opt)
            self.btn_group.addButton(rb)
            self.option_btns.append(rb)
            q_lay.addWidget(rb)

        root.addWidget(self.q_card)

        # Navigation
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("◀  Previous")
        self.btn_prev.setObjectName("btnSecondary")
        self.btn_prev.setFixedWidth(130)
        self.btn_prev.clicked.connect(self._prev_q)

        self.btn_skip = QPushButton("Skip  ⟶")
        self.btn_skip.setObjectName("btnWarning")
        self.btn_skip.setFixedWidth(110)
        self.btn_skip.clicked.connect(self._skip_q)

        self.btn_next = QPushButton("Next  ▶")
        self.btn_next.setObjectName("btnPrimary")
        self.btn_next.setFixedWidth(110)
        self.btn_next.clicked.connect(self._next_q)

        self.btn_submit = QPushButton("✔  Submit Exam")
        self.btn_submit.setObjectName("btnSuccess")
        self.btn_submit.setFixedWidth(150)
        self.btn_submit.clicked.connect(self._confirm_submit)

        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_skip)
        nav.addStretch()
        nav.addWidget(self.btn_next)
        nav.addSpacing(12)
        nav.addWidget(self.btn_submit)
        root.addLayout(nav)

        # Question navigator dots
        self.nav_frame = QFrame()
        self.nav_frame.setObjectName("card")
        nav_inner = QHBoxLayout(self.nav_frame)
        nav_inner.setContentsMargins(14, 10, 14, 10)
        nav_inner.setSpacing(6)
        self.dot_buttons = []
        for i in range(len(self.questions)):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(34, 34)
            btn.setStyleSheet(self._dot_style("unanswered"))
            btn.clicked.connect(lambda _, idx=i: self._jump_to(idx))
            self.dot_buttons.append(btn)
            nav_inner.addWidget(btn)
        nav_inner.addStretch()
        root.addWidget(self.nav_frame)

    # ── Question loading ────────────────────────────────
    def _load_question(self, idx):
        if not self.questions:
            return
        q = self.questions[idx]
        self.lbl_qnum.setText(f"Question {idx + 1} of {len(self.questions)}")
        self.lbl_subject.setText(q["subject"].upper())
        self.lbl_question.setText(q["question"])
        opts = [("A", q["option_a"]), ("B", q["option_b"]),
                ("C", q["option_c"]), ("D", q["option_d"])]
        for rb, (key, text) in zip(self.option_btns, opts):
            rb.setText(f"  {key}.  {text}")
            rb.setProperty("opt_key", key)

        # Restore saved answer
        self.btn_group.setExclusive(False)
        for rb in self.option_btns:
            rb.setChecked(False)
        self.btn_group.setExclusive(True)

        saved = self.answers.get(idx)
        if saved and saved != "S":
            for rb in self.option_btns:
                if rb.property("opt_key") == saved:
                    rb.setChecked(True)

        self.progress.setValue(idx + 1)
        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setEnabled(idx < len(self.questions) - 1)
        self._refresh_dots()

    def _save_current_answer(self):
        checked = self.btn_group.checkedButton()
        if checked:
            self.answers[self.current_q] = checked.property("opt_key")

    # ── Navigation ──────────────────────────────────────
    def _prev_q(self):
        self._save_current_answer()
        if self.current_q > 0:
            self.current_q -= 1
            self._load_question(self.current_q)

    def _next_q(self):
        self._save_current_answer()
        if self.current_q < len(self.questions) - 1:
            self.current_q += 1
            self._load_question(self.current_q)

    def _skip_q(self):
        self.answers[self.current_q] = "S"
        self.btn_group.setExclusive(False)
        for rb in self.option_btns: rb.setChecked(False)
        self.btn_group.setExclusive(True)
        self._refresh_dots()
        if self.current_q < len(self.questions) - 1:
            self.current_q += 1
            self._load_question(self.current_q)

    def _jump_to(self, idx):
        self._save_current_answer()
        self.current_q = idx
        self._load_question(idx)

    # ── Timer ───────────────────────────────────────────
    def _tick(self):
        self.time_left -= 1
        m, s = divmod(self.time_left, 60)
        self.lbl_timer.setText(f"{m:02d}:{s:02d}")
        if self.time_left <= 60:
            self.lbl_timer.setStyleSheet(EXAM_TIMER_STYLE_DANGER)
        elif self.time_left <= 300:
            self.lbl_timer.setStyleSheet(EXAM_TIMER_STYLE_WARNING)
        if self.time_left <= 0:
            self.timer.stop()
            QMessageBox.warning(self, "Time Up!", "Time is up! Submitting your exam.")
            self._submit_exam()

    # ── Submit ──────────────────────────────────────────
    def _confirm_submit(self):
        unanswered = sum(
            1 for i in range(len(self.questions)) if i not in self.answers
        )
        msg = f"Submit exam?\n\nAnswered: {len(self.questions) - unanswered}\nUnanswered: {unanswered}"
        reply = QMessageBox.question(self, "Confirm Submit", msg,
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._save_current_answer()
            self._submit_exam()

    def _submit_exam(self):
        if self.submitted:
            return
        self.submitted = True
        self.timer.stop()

        score = correct = wrong = skipped = 0
        details = []
        for i, q in enumerate(self.questions):
            ans = self.answers.get(i, "S")
            if ans == "S":
                skipped += 1
                status = "Skipped"
            elif ans == q["answer"]:
                score += 4; correct += 1; status = "Correct"
            else:
                score -= 1; wrong += 1; status = "Wrong"
            details.append({
                "question":       q["question"],
                "student_answer": ans,
                "correct_answer": q["answer"],
                "status":         status
            })

        total       = len(self.questions)
        percentage  = round((score / (total * 4)) * 100, 2)
        grade       = calculate_grade(percentage)

        result_id = save_result(
            self.student["student_id"], self.student["full_name"],
            score, correct, wrong, skipped, total, percentage, grade, details
        )

        self.close()
        result_data = {
            "student_name": self.student["full_name"],
            "student_id":   self.student["student_id"],
            "score": score, "correct": correct, "wrong": wrong,
            "skipped": skipped, "total": total,
            "percentage": percentage, "grade": grade,
            "details": details, "result_id": result_id
        }
        self.result_win = ResultWindow(result_data, self.parent_db)
        self.result_win.show()

    # ── Dot styles ──────────────────────────────────────
    def _dot_style(self, state):
        colors = {
            "current":    (BLUE,   WHITE),
            "answered":   (GREEN,  WHITE),
            "skipped":    (ORANGE, WHITE),
            "unanswered": (WHITE,  "#555"),
        }
        bg, fg = colors.get(state, (WHITE, "#555"))
        return (f"QPushButton{{background:{bg};color:{fg};border:1.5px solid {BORDER};"
                f"border-radius:17px;font-size:11px;font-weight:bold;}}"
                f"QPushButton:hover{{background:{BLUE_D};color:white;}}")

    def _refresh_dots(self):
        for i, btn in enumerate(self.dot_buttons):
            if i == self.current_q:
                btn.setStyleSheet(self._dot_style("current"))
            elif self.answers.get(i) == "S":
                btn.setStyleSheet(self._dot_style("skipped"))
            elif i in self.answers:
                btn.setStyleSheet(self._dot_style("answered"))
            else:
                btn.setStyleSheet(self._dot_style("unanswered"))


# ══════════════════════════════════════════════════════════
#  RESULT WINDOW
# ══════════════════════════════════════════════════════════

class ResultWindow(QMainWindow):
    def __init__(self, result, parent_dashboard=None):
        super().__init__()
        self.result     = result
        self.parent_db  = parent_dashboard
        self.setWindowTitle("Exam Result")
        self.setMinimumSize(760, 580)
        self.setStyleSheet(DASH_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(16)

        # Title
        r = self.result
        grade_color = {
            "EXCELLENT": GREEN, "GOOD": BLUE,
            "AVERAGE": ORANGE, "BELOW AVERAGE": RED
        }.get(r["grade"], BLUE)

        title = QLabel("📊  Exam Result")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        root.addWidget(title)

        # Stat cards
        cards = QHBoxLayout()
        cards.setSpacing(12)
        cards.addWidget(StatCard("SCORE",      f"{r['score']} / {r['total']*4}", BLUE))
        cards.addWidget(StatCard("PERCENTAGE", f"{r['percentage']}%",            grade_color))
        cards.addWidget(StatCard("CORRECT",    str(r["correct"]),                GREEN))
        cards.addWidget(StatCard("WRONG",      str(r["wrong"]),                  RED))
        cards.addWidget(StatCard("SKIPPED",    str(r["skipped"]),                ORANGE))
        root.addLayout(cards)

        # Grade banner
        grade_banner = QLabel(f"Grade:  {r['grade']}")
        grade_banner.setAlignment(Qt.AlignCenter)
        grade_banner.setStyleSheet(
            f"font-size:22px; font-weight:bold; color:{grade_color};"
            f"background:white; border-radius:12px; padding:12px;"
            f"border:2px solid {grade_color};"
        )
        root.addWidget(grade_banner)

        # Detailed answers table
        lbl = QLabel("Detailed Answer Review")
        lbl.setStyleSheet("font-size:15px; font-weight:bold;")
        root.addWidget(lbl)

        table = make_table(["#", "Question", "Your Answer", "Correct Answer", "Status"])
        table.setRowCount(len(r["details"]))
        status_colors = {"Correct": GREEN, "Wrong": RED, "Skipped": ORANGE}
        for ri, d in enumerate(r["details"]):
            vals = [str(ri+1), d["question"], d["student_answer"],
                    d["correct_answer"], d["status"]]
            for ci, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if ci == 4:
                    item.setForeground(QColor(status_colors.get(d["status"], GREY)))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                table.setItem(ri, ci, item)
        root.addWidget(table)

        # Buttons
        btns = QHBoxLayout()
        btn_back = QPushButton("← Back to Dashboard")
        btn_back.setObjectName("btnSecondary")
        btn_back.setFixedWidth(200)
        btn_back.clicked.connect(self._go_back)
        btns.addStretch()
        btns.addWidget(btn_back)
        root.addLayout(btns)

    def _go_back(self):
        self.close()
        if self.parent_db:
            self.parent_db.show()
            self.parent_db.refresh_results()


# ══════════════════════════════════════════════════════════
#  STUDENT DASHBOARD
# ══════════════════════════════════════════════════════════

class StudentDashboard(QMainWindow):
    def __init__(self, student_data):
        super().__init__()
        self.student = student_data
        self.setWindowTitle("UET University — Student Portal")
        self.setMinimumSize(800, 580)
        self.setStyleSheet(DASH_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(18)

        # Header
        hdr = QHBoxLayout()
        lbl_t = QLabel("🎓  Student Portal")
        lbl_t.setStyleSheet("font-size:20px; font-weight:bold;")
        lbl_u = QLabel(f"Welcome, {self.student['full_name']}")
        lbl_u.setStyleSheet(f"font-size:13px; color:{GREY};")
        btn_out = QPushButton("Logout")
        btn_out.setObjectName("btnDanger")
        btn_out.setFixedWidth(90)
        btn_out.clicked.connect(self._logout)
        hdr.addWidget(lbl_t); hdr.addStretch()
        hdr.addWidget(lbl_u); hdr.addSpacing(12); hdr.addWidget(btn_out)
        root.addLayout(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#dde1ea;"); root.addWidget(sep)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_overview_tab(), "📋  Overview")
        tabs.addTab(self._build_exam_tab(),     "📝  Take Exam")
        tabs.addTab(self._build_results_tab(),  "📊  My Results")
        root.addWidget(tabs)

    # ── Overview tab ────────────────────────────────────
    def _build_overview_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0); lay.setSpacing(14)

        results = get_student_results(self.student["student_id"])

        cards = QHBoxLayout(); cards.setSpacing(14)
        cards.addWidget(StatCard("STUDENT ID",   self.student["student_id"],   BLUE))
        cards.addWidget(StatCard("DEPARTMENT",   self.student["department"],   GREEN))
        cards.addWidget(StatCard("SEMESTER",     str(self.student["semester"]),PURPLE))
        cards.addWidget(StatCard("EXAMS TAKEN",  str(len(results)),            ORANGE))
        lay.addLayout(cards)

        prof = QFrame(); prof.setObjectName("card")
        pl = QGridLayout(prof); pl.setContentsMargins(20,16,20,16)
        pl.setHorizontalSpacing(16); pl.setVerticalSpacing(10)
        sec = QLabel("Profile Information")
        sec.setStyleSheet("font-size:15px; font-weight:bold;")
        pl.addWidget(sec, 0, 0, 1, 4)
        fields = [("Full Name", self.student["full_name"]),
                  ("Email",     self.student["email"]),
                  ("Department",self.student["department"]),
                  ("Semester",  str(self.student["semester"])),
                  ("Enrolled",  self.student["created_at"][:10])]
        for i, (lbl, val) in enumerate(fields):
            r, col = (i // 2) + 1, (i % 2) * 2
            l = QLabel(lbl + ":"); l.setStyleSheet(f"font-size:12px; color:{GREY}; font-weight:bold;")
            v = QLabel(val);       v.setStyleSheet("font-size:13px;")
            pl.addWidget(l, r, col); pl.addWidget(v, r, col+1)
        lay.addWidget(prof)

        btns = QHBoxLayout()
        btn_pw = QPushButton("🔑  Change Password")
        btn_pw.setObjectName("btnSecondary"); btn_pw.setFixedWidth(180)
        btn_pw.clicked.connect(self._change_password)
        btns.addWidget(btn_pw); btns.addStretch()
        lay.addLayout(btns); lay.addStretch()
        return w

    # ── Exam tab ─────────────────────────────────────────
    def _build_exam_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 20, 0, 0); lay.setSpacing(14)

        # Rules card
        rules_card = QFrame(); rules_card.setObjectName("card")
        rl = QVBoxLayout(rules_card); rl.setContentsMargins(22, 18, 22, 18)
        rl.addWidget(QLabel("📋  Exam Rules"))
        rules_card.findChildren(QLabel)[0].setStyleSheet(
            "font-size:15px; font-weight:bold;")
        rules = [
            "✦  Total questions: " + str(len(get_questions())),
            "✦  Time allowed: 20 minutes",
            "✦  Each correct answer: +4 marks",
            "✦  Each wrong answer: −1 mark",
            "✦  Skipped questions: 0 marks",
            "✦  You can navigate between questions freely",
            "✦  Click 'Skip' to mark a question for later",
            "✦  Exam auto-submits when time runs out",
        ]
        for rule in rules:
            lbl = QLabel(rule)
            lbl.setStyleSheet(f"font-size:13px; color:#333; padding:2px 0;")
            rl.addWidget(lbl)

        lay.addWidget(rules_card)

        btn_start = QPushButton("🚀  Start ECAT Exam")
        btn_start.setObjectName("btnSuccess")
        btn_start.setFixedHeight(52)
        btn_start.setStyleSheet(
            "QPushButton{background:#2e7d32;color:white;border:none;"
            "border-radius:12px;font-size:15px;font-weight:bold;}"
            "QPushButton:hover{background:#1b5e20;}"
        )
        btn_start.clicked.connect(self._start_exam)
        lay.addWidget(btn_start)
        lay.addStretch()
        return w

    # ── Results tab ──────────────────────────────────────
    def _build_results_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0); lay.setSpacing(10)
        lbl = QLabel("My Exam History")
        lbl.setStyleSheet("font-size:15px; font-weight:bold;")
        lay.addWidget(lbl)
        self.my_results_table = make_table(
            ["#", "Score", "Correct", "Wrong", "Skipped", "Percentage", "Grade", "Date"])
        lay.addWidget(self.my_results_table)
        self.refresh_results()

        btn_review = QPushButton("🔍  Review Selected Exam")
        btn_review.setObjectName("btnSecondary"); btn_review.setFixedWidth(200)
        btn_review.clicked.connect(self._review_selected)
        lay.addWidget(btn_review, alignment=Qt.AlignLeft)
        return w

    def refresh_results(self):
        results = get_student_results(self.student["student_id"])
        self.my_results_table.setRowCount(len(results))
        grade_colors = {"EXCELLENT": GREEN, "GOOD": BLUE,
                        "AVERAGE": ORANGE, "BELOW AVERAGE": RED}
        for ri, r in enumerate(results):
            vals = [str(ri+1), f"{r['score']}/{r['total_questions']*4}",
                    str(r["correct"]), str(r["wrong"]), str(r["skipped"]),
                    f"{r['percentage']}%", r["grade"], r["exam_date"]]
            for ci, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if ci == 6:
                    item.setForeground(QColor(grade_colors.get(r["grade"], GREY)))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.my_results_table.setItem(ri, ci, item)
        # Store result ids for review
        self._result_list = results

    def _review_selected(self):
        row = self.my_results_table.currentRow()
        if row < 0 or not hasattr(self, '_result_list') or row >= len(self._result_list):
            QMessageBox.information(self, "Select Row", "Please select an exam row to review.")
            return
        r = self._result_list[row]
        details = get_result_details(r["id"])
        result_data = {
            "student_name": r["student_name"],
            "student_id":   r["student_id"],
            "score": r["score"], "correct": r["correct"],
            "wrong": r["wrong"], "skipped": r["skipped"],
            "total": r["total_questions"],
            "percentage": r["percentage"], "grade": r["grade"],
            "details": details, "result_id": r["id"]
        }
        self.review_win = ResultWindow(result_data, self)
        self.review_win.show()
        self.hide()

    # ── Handlers ─────────────────────────────────────────
    def _start_exam(self):
        if not get_questions():
            QMessageBox.warning(self, "No Questions",
                                "No questions in the question bank. Contact admin.")
            return
        reply = QMessageBox.question(self, "Start Exam",
            "Are you ready to start the ECAT exam?\nTimer will begin immediately.",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.hide()
            self.exam_win = ExamWindow(self.student, parent_dashboard=self)
            self.exam_win.show()

    def _change_password(self):
        pw, ok = QInputDialog.getText(self, "Change Password",
                                      "New password:", QLineEdit.Password)
        if ok and pw.strip():
            if len(pw) < 6:
                QMessageBox.warning(self, "Weak", "Min 6 characters required.")
                return
            if reset_password(self.student["student_id"], "student", pw):
                QMessageBox.information(self, "Done", "Password updated!")

    def _logout(self):
        self.close()
        login_window.show()


# ══════════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════

class AdminDashboard(QMainWindow):
    def __init__(self, admin_data):
        super().__init__()
        self.admin = admin_data
        self.setWindowTitle("UET University — Admin Portal")
        self.setMinimumSize(980, 660)
        self.setStyleSheet(DASH_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(18)

        # Header
        hdr = QHBoxLayout()
        lbl_t = QLabel("👤  Admin Panel")
        lbl_t.setStyleSheet("font-size:20px; font-weight:bold;")
        lbl_u = QLabel(f"{self.admin['full_name']}  ·  {self.admin['role']}")
        lbl_u.setStyleSheet(f"font-size:13px; color:{GREY};")
        btn_out = QPushButton("Logout")
        btn_out.setObjectName("btnDanger"); btn_out.setFixedWidth(90)
        btn_out.clicked.connect(self._logout)
        hdr.addWidget(lbl_t); hdr.addStretch()
        hdr.addWidget(lbl_u); hdr.addSpacing(12); hdr.addWidget(btn_out)
        root.addLayout(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#dde1ea;"); root.addWidget(sep)

        # Stat cards
        students = get_all_students()
        results  = get_all_results()
        questions = get_questions()
        cards = QHBoxLayout(); cards.setSpacing(14)
        cards.addWidget(StatCard("STUDENTS",   str(len(students)),   BLUE))
        cards.addWidget(StatCard("QUESTIONS",  str(len(questions)),  GREEN))
        cards.addWidget(StatCard("EXAMS TAKEN",str(len(results)),    PURPLE))
        pass_c = sum(1 for r in results if r["percentage"] >= 50)
        cards.addWidget(StatCard("PASS RATE",
            f"{round(pass_c/len(results)*100)}%" if results else "N/A", ORANGE))
        root.addLayout(cards)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_students_tab(),   "🎓  Students")
        tabs.addTab(self._build_questions_tab(),  "❓  Questions")
        tabs.addTab(self._build_results_tab(),    "📊  Results")
        tabs.addTab(self._build_logs_tab(),       "📋  Logs")
        root.addWidget(tabs)

    # ── Students tab ────────────────────────────────────
    def _build_students_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(0,12,0,0); lay.setSpacing(10)
        tb = QHBoxLayout()
        lbl = QLabel("Registered Students")
        lbl.setStyleSheet("font-size:15px; font-weight:bold;")
        btn_add = QPushButton("+ Add Student")
        btn_add.setObjectName("btnPrimary"); btn_add.setFixedWidth(130)
        btn_add.clicked.connect(self._add_student)
        btn_ref = QPushButton("↻ Refresh")
        btn_ref.setObjectName("btnSecondary"); btn_ref.setFixedWidth(100)
        btn_ref.clicked.connect(self._refresh_students)
        tb.addWidget(lbl); tb.addStretch(); tb.addWidget(btn_ref); tb.addWidget(btn_add)
        lay.addLayout(tb)
        self.students_table = make_table(
            ["Student ID", "Full Name", "Email", "Department", "Semester", "Enrolled"])
        lay.addWidget(self.students_table)
        self._refresh_students()
        return w

    def _refresh_students(self):
        fill_table(self.students_table, get_all_students(),
                   ["student_id","full_name","email","department","semester","created_at"],
                   {"created_at": lambda v: v[:10]})

    def _add_student(self):
        fields = [("Student ID (e.g. STU004)",""),("Full Name",""),
                  ("Email",""),("Department",""),("Semester (1-8)",""),("Password","")]
        vals = []
        for prompt, _ in fields:
            echo = QLineEdit.Password if "Password" in prompt else QLineEdit.Normal
            v, ok = QInputDialog.getText(self, "Add Student", prompt + ":", echo)
            if not ok: return
            vals.append(v.strip())
        sid, name, email, dept, sem, pw = vals
        if not all([sid, name, email, dept, sem, pw]):
            QMessageBox.warning(self, "Incomplete", "All fields required."); return
        if not sem.isdigit() or not 1 <= int(sem) <= 8:
            QMessageBox.warning(self, "Invalid", "Semester must be 1–8."); return
        ok, msg = add_student_db(sid, name, email, dept, int(sem), pw)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self._refresh_students()
        else:
            QMessageBox.critical(self, "Error", msg)

    # ── Questions tab ────────────────────────────────────
    def _build_questions_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(0,12,0,0); lay.setSpacing(10)
        tb = QHBoxLayout()
        lbl = QLabel("Question Bank")
        lbl.setStyleSheet("font-size:15px; font-weight:bold;")
        btn_add = QPushButton("+ Add Question")
        btn_add.setObjectName("btnPrimary"); btn_add.setFixedWidth(140)
        btn_add.clicked.connect(self._add_question)
        btn_del = QPushButton("🗑 Delete")
        btn_del.setObjectName("btnDanger"); btn_del.setFixedWidth(90)
        btn_del.clicked.connect(self._delete_question)
        btn_edit = QPushButton("✏ Edit")
        btn_edit.setObjectName("btnWarning"); btn_edit.setFixedWidth(80)
        btn_edit.clicked.connect(self._edit_question)
        btn_ref = QPushButton("↻")
        btn_ref.setObjectName("btnSecondary"); btn_ref.setFixedWidth(46)
        btn_ref.clicked.connect(self._refresh_questions)
        tb.addWidget(lbl); tb.addStretch()
        tb.addWidget(btn_ref); tb.addWidget(btn_edit)
        tb.addWidget(btn_del); tb.addWidget(btn_add)
        lay.addLayout(tb)
        self.q_table = make_table(
            ["ID","Subject","Question","A","B","C","D","Answer"])
        lay.addWidget(self.q_table)
        self._refresh_questions()
        return w

    def _refresh_questions(self):
        qs = get_questions()
        self.q_table.setRowCount(len(qs))
        for ri, q in enumerate(qs):
            for ci, key in enumerate(["id","subject","question",
                                       "option_a","option_b","option_c","option_d","answer"]):
                item = QTableWidgetItem(str(q[key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.q_table.setItem(ri, ci, item)
        self._questions_cache = qs

    def _add_question(self):
        fields = ["Subject","Question","Option A","Option B",
                  "Option C","Option D","Correct Answer (A/B/C/D)"]
        vals = []
        for f in fields:
            v, ok = QInputDialog.getText(self, "Add Question", f + ":")
            if not ok: return
            vals.append(v.strip())
        subj, q, a, b, c, d, ans = vals
        ans = ans.upper()
        if not all([subj, q, a, b, c, d]):
            QMessageBox.warning(self, "Incomplete", "All fields required."); return
        if ans not in ["A","B","C","D"]:
            QMessageBox.warning(self, "Invalid", "Answer must be A, B, C, or D."); return
        ok, msg = add_question_db(subj, q, a, b, c, d, ans)
        if ok:
            QMessageBox.information(self, "Added", msg)
            self._refresh_questions()
        else:
            QMessageBox.critical(self, "Error", msg)

    def _delete_question(self):
        row = self.q_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select", "Select a question first."); return
        qid = int(self.q_table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirm", "Delete this question?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_question_db(qid)
            self._refresh_questions()

    def _edit_question(self):
        row = self.q_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select", "Select a question first."); return
        q = self._questions_cache[row]
        fields = [("Subject", q["subject"]), ("Question", q["question"]),
                  ("Option A", q["option_a"]), ("Option B", q["option_b"]),
                  ("Option C", q["option_c"]), ("Option D", q["option_d"]),
                  ("Answer (A/B/C/D)", q["answer"])]
        vals = []
        for prompt, default in fields:
            v, ok = QInputDialog.getText(self, "Edit Question", prompt + ":", text=default)
            if not ok: return
            vals.append(v.strip())
        subj, ques, a, b, c, d, ans = vals
        ans = ans.upper()
        if ans not in ["A","B","C","D"]:
            QMessageBox.warning(self, "Invalid", "Answer must be A, B, C, or D."); return
        update_question_db(q["id"], subj, ques, a, b, c, d, ans)
        QMessageBox.information(self, "Updated", "Question updated.")
        self._refresh_questions()

    # ── Results tab ──────────────────────────────────────
    def _build_results_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(0,12,0,0); lay.setSpacing(10)
        tb = QHBoxLayout()
        lbl = QLabel("All Student Results")
        lbl.setStyleSheet("font-size:15px; font-weight:bold;")
        btn_ref = QPushButton("↻ Refresh")
        btn_ref.setObjectName("btnSecondary"); btn_ref.setFixedWidth(100)
        btn_ref.clicked.connect(self._refresh_results)
        btn_view = QPushButton("🔍 Review Selected")
        btn_view.setObjectName("btnPrimary"); btn_view.setFixedWidth(160)
        btn_view.clicked.connect(self._admin_review_result)
        tb.addWidget(lbl); tb.addStretch(); tb.addWidget(btn_ref); tb.addWidget(btn_view)
        lay.addLayout(tb)
        self.results_table = make_table(
            ["#","Student ID","Name","Score","Correct","Wrong","Skipped","Percentage","Grade","Date"])
        lay.addWidget(self.results_table)
        self._refresh_results()
        return w

    def _refresh_results(self):
        results = get_all_results()
        self.results_table.setRowCount(len(results))
        grade_colors = {"EXCELLENT": GREEN, "GOOD": BLUE,
                        "AVERAGE": ORANGE, "BELOW AVERAGE": RED}
        for ri, r in enumerate(results):
            vals = [str(ri+1), r["student_id"], r["student_name"],
                    f"{r['score']}/{r['total_questions']*4}",
                    str(r["correct"]), str(r["wrong"]), str(r["skipped"]),
                    f"{r['percentage']}%", r["grade"], r["exam_date"]]
            for ci, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if ci == 8:
                    item.setForeground(QColor(grade_colors.get(r["grade"], GREY)))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.results_table.setItem(ri, ci, item)
        self._results_cache = results

    def _admin_review_result(self):
        row = self.results_table.currentRow()
        if row < 0 or not hasattr(self,"_results_cache") or row >= len(self._results_cache):
            QMessageBox.information(self, "Select", "Select a result row first."); return
        r = self._results_cache[row]
        details = get_result_details(r["id"])
        result_data = {
            "student_name": r["student_name"], "student_id": r["student_id"],
            "score": r["score"], "correct": r["correct"], "wrong": r["wrong"],
            "skipped": r["skipped"], "total": r["total_questions"],
            "percentage": r["percentage"], "grade": r["grade"],
            "details": details, "result_id": r["id"]
        }
        self.review_win = ResultWindow(result_data)
        self.review_win.show()

    # ── Logs tab ─────────────────────────────────────────
    def _build_logs_tab(self):
        w = QWidget(); lay = QVBoxLayout(w)
        lay.setContentsMargins(0,12,0,0); lay.setSpacing(10)
        lbl = QLabel("Recent Login Attempts (last 50)")
        lbl.setStyleSheet("font-size:15px; font-weight:bold;")
        lay.addWidget(lbl)
        conn = get_conn()
        logs = conn.execute(
            "SELECT user_id,user_type,status,timestamp FROM login_logs ORDER BY id DESC LIMIT 50"
        ).fetchall()
        conn.close()
        table = make_table(["User ID","Type","Status","Timestamp"])
        table.setRowCount(len(logs))
        for ri, log in enumerate(logs):
            for ci, key in enumerate(["user_id","user_type","status","timestamp"]):
                item = QTableWidgetItem(str(log[key]))
                item.setTextAlignment(Qt.AlignCenter)
                if key == "status":
                    item.setForeground(QColor(GREEN if log[key]=="success" else RED))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                table.setItem(ri, ci, item)
        lay.addWidget(table)
        return w

    def refresh_results(self):
        self._refresh_results()

    def _logout(self):
        self.close()
        login_window.show()


# ══════════════════════════════════════════════════════════
#  LOGIN DIALOG
# ══════════════════════════════════════════════════════════

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UET University - Portal Login")
        self.setFixedSize(420, 540)
        self.setStyleSheet(LOGIN_STYLE)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._build_ui()

    def _build_ui(self):
        self.btnClose = QPushButton("✕", self)
        self.btnClose.setObjectName("btnClose")
        self.btnClose.setGeometry(14, 14, 32, 32)
        self.btnClose.setCursor(Qt.PointingHandCursor)
        self.btnClose.clicked.connect(self.close)

        self.lblLogo = QLabel("🎓", self)
        self.lblLogo.setGeometry(183, 50, 54, 54)
        self.lblLogo.setAlignment(Qt.AlignCenter)
        self.lblLogo.setStyleSheet(
            "background:#1565C0; border-radius:14px; font-size:26px;")

        lbl_name = QLabel("UET University", self)
        lbl_name.setObjectName("lblUniversityName")
        lbl_name.setGeometry(30, 114, 360, 32)
        lbl_name.setAlignment(Qt.AlignCenter)

        lbl_sub = QLabel("Portal Login", self)
        lbl_sub.setObjectName("lblPortalSub")
        lbl_sub.setGeometry(30, 148, 360, 20)
        lbl_sub.setAlignment(Qt.AlignCenter)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setGeometry(30, 182, 360, 300)

        # Student tab
        ts = QWidget(); self.tabWidget.addTab(ts, "🎓  STUDENT")

        self.txtStudentID = QLineEdit(ts)
        self.txtStudentID.setGeometry(0, 20, 360, 48)
        self.txtStudentID.setPlaceholderText("Student ID *")

        self.txtStudentPassword = QLineEdit(ts)
        self.txtStudentPassword.setGeometry(0, 82, 360, 48)
        self.txtStudentPassword.setPlaceholderText("Password *")
        self.txtStudentPassword.setEchoMode(QLineEdit.Password)

        self.btnLoginStudent = QPushButton("LOGIN AS STUDENT", ts)
        self.btnLoginStudent.setObjectName("btnLoginStudent")
        self.btnLoginStudent.setGeometry(0, 146, 360, 50)
        self.btnLoginStudent.setCursor(Qt.PointingHandCursor)
        self.btnLoginStudent.clicked.connect(self._login_student)

        btn_fp_s = QPushButton("Forgot Password?", ts)
        btn_fp_s.setObjectName("btnForgotPassword")
        btn_fp_s.setGeometry(0, 210, 360, 30)
        btn_fp_s.setCursor(Qt.PointingHandCursor)
        btn_fp_s.clicked.connect(lambda: self._forgot("student"))

        # Admin tab
        ta = QWidget(); self.tabWidget.addTab(ta, "👤  ADMIN")

        self.txtAdminID = QLineEdit(ta)
        self.txtAdminID.setGeometry(0, 20, 360, 48)
        self.txtAdminID.setPlaceholderText("Admin ID *")

        self.txtAdminPassword = QLineEdit(ta)
        self.txtAdminPassword.setGeometry(0, 82, 360, 48)
        self.txtAdminPassword.setPlaceholderText("Password *")
        self.txtAdminPassword.setEchoMode(QLineEdit.Password)

        self.btnLoginAdmin = QPushButton("LOGIN AS ADMIN", ta)
        self.btnLoginAdmin.setObjectName("btnLoginAdmin")
        self.btnLoginAdmin.setGeometry(0, 146, 360, 50)
        self.btnLoginAdmin.setCursor(Qt.PointingHandCursor)
        self.btnLoginAdmin.clicked.connect(self._login_admin)

        btn_fp_a = QPushButton("Forgot Password?", ta)
        btn_fp_a.setObjectName("btnForgotPasswordAdmin")
        btn_fp_a.setGeometry(0, 210, 360, 30)
        btn_fp_a.setCursor(Qt.PointingHandCursor)
        btn_fp_a.clicked.connect(lambda: self._forgot("admin"))

        self.txtStudentPassword.returnPressed.connect(self._login_student)
        self.txtAdminPassword.returnPressed.connect(self._login_admin)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and hasattr(self, '_drag'):
            self.move(e.globalPos() - self._drag)

    def _login_student(self):
        sid = self.txtStudentID.text().strip()
        pwd = self.txtStudentPassword.text()
        if not sid or not pwd:
            QMessageBox.warning(self, "Missing", "Enter Student ID and Password."); return
        row = auth_student(sid, pwd)
        if row:
            log_login(sid, "student", "success")
            self.hide()
            global student_dashboard
            student_dashboard = StudentDashboard(dict(row))
            student_dashboard.show()
        else:
            log_login(sid, "student", "failed")
            QMessageBox.critical(self, "Failed", "Invalid Student ID or Password.")
            self.txtStudentPassword.clear(); self.txtStudentPassword.setFocus()

    def _login_admin(self):
        aid = self.txtAdminID.text().strip()
        pwd = self.txtAdminPassword.text()
        if not aid or not pwd:
            QMessageBox.warning(self, "Missing", "Enter Admin ID and Password."); return
        row = auth_admin(aid, pwd)
        if row:
            log_login(aid, "admin", "success")
            self.hide()
            global admin_dashboard
            admin_dashboard = AdminDashboard(dict(row))
            admin_dashboard.show()
        else:
            log_login(aid, "admin", "failed")
            QMessageBox.critical(self, "Failed", "Invalid Admin ID or Password.")
            self.txtAdminPassword.clear(); self.txtAdminPassword.setFocus()

    def _forgot(self, utype):
        uid, ok = QInputDialog.getText(
            self, "Reset Password",
            f"Enter your {'Student' if utype=='student' else 'Admin'} ID:")
        if not ok or not uid.strip(): return
        pw, ok2 = QInputDialog.getText(
            self, "New Password", "Enter new password:", QLineEdit.Password)
        if not ok2 or not pw.strip(): return
        if len(pw) < 6:
            QMessageBox.warning(self, "Weak", "Min 6 characters."); return
        if reset_password(uid.strip(), utype, pw):
            QMessageBox.information(self, "Done", "Password reset successfully!")
        else:
            QMessageBox.critical(self, "Not Found", f"No account with ID: {uid.strip()}")


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════

login_window      = None
student_dashboard = None
admin_dashboard   = None


def main():
    global login_window
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName("UET University ECAT Portal")
    login_window = LoginDialog()
    login_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

