"""
Seed script: populates library.db with rich demo data for interview presentation.
Run: python seed_demo_data.py
"""
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

DB = "library.db"

# ── helpers ──────────────────────────────────────────────────────────────
def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def delete_all(db):
    db.execute("DELETE FROM transactions")
    db.execute("DELETE FROM books")
    db.execute("DELETE FROM users WHERE username != 'admin'")
    db.execute("UPDATE users SET password=? WHERE username='admin'",
               (generate_password_hash("admin123"),))

# ── data sets ────────────────────────────────────────────────────────────
STUDENTS = [
    ("aryan_sharma", "aryan.sharma@harrow.edu", "student"),
    ("priya_verma", "priya.verma@harrow.edu", "student"),
    ("rohit_kumar", "rohit.kumar@harrow.edu", "student"),
    ("sneha_patel", "sneha.patel@harrow.edu", "student"),
    ("amit_singh", "amit.singh@harrow.edu", "student"),
    ("neha_jain", "neha.jain@harrow.edu", "student"),
    ("vikram_rao", "vikram.rao@harrow.edu", "student"),
    ("ananya_gupta", "ananya.gupta@harrow.edu", "student"),
    ("rahul_desai", "rahul.desai@harrow.edu", "student"),
    ("kriti_agarwal", "kriti.agarwal@harrow.edu", "student"),
    ("manoj_yadav", "manoj.yadav@harrow.edu", "student"),
    ("deepika_nair", "deepika.nair@harrow.edu", "student"),
    ("sandeep_thakur", "sandeep.thakur@harrow.edu", "student"),
    ("pallavi_joshi", "pallavi.joshi@harrow.edu", "student"),
    ("harsh_mishra", "harsh.mishra@harrow.edu", "student"),
    ("tarun_mehta", "tarun.mehta@harrow.edu", "student"),
    ("kavya_iyer", "kavya.iyer@harrow.edu", "student"),
    ("sahil_khan", "sahil.khan@harrow.edu", "student"),
    ("ishita_chopra", "ishita.chopra@harrow.edu", "student"),
    ("akash_bhat", "akash.bhat@harrow.edu", "student"),
    ("nidhi_saxena", "nidhi.saxena@harrow.edu", "student"),
    ("prateek_sethi", "prateek.sethi@harrow.edu", "student"),
    ("divya_pillai", "divya.pillai@harrow.edu", "student"),
    ("kunal_dogra", "kunal.dogra@harrow.edu", "student"),
]

BOOKS = [
    # (title, author, isbn, subject, class_level, stream, book_type, publisher, total_copies, shelf_block, shelf_row, shelf_col)
    ("Mathematics Textbook Class 10", "NCERT", "9788174506344", "Mathematics", "10", "General", "NCERT", "NCERT", 15, "A", "1", "1"),
    ("Science Textbook Class 10", "NCERT", "9788174506443", "Science", "10", "General", "NCERT", "NCERT", 15, "A", "1", "2"),
    ("First Flight (English Reader)", "NCERT", "9788174506542", "English", "10", "General", "NCERT", "NCERT", 12, "A", "1", "3"),
    ("Physics Part 1 Class 11", "NCERT", "9788174506641", "Physics", "11", "PCM", "NCERT", "NCERT", 10, "A", "2", "1"),
    ("Chemistry Part 1 Class 11", "NCERT", "9788174506740", "Chemistry", "11", "PCM", "NCERT", "NCERT", 10, "A", "2", "2"),
    ("Mathematics Class 11", "NCERT", "9788174506849", "Mathematics", "11", "PCM", "NCERT", "NCERT", 10, "A", "2", "3"),
    ("Physics Part 2 Class 12", "NCERT", "9788174506948", "Physics", "12", "PCM", "NCERT", "NCERT", 8, "A", "3", "1"),
    ("Chemistry Part 2 Class 12", "NCERT", "9788174507044", "Chemistry", "12", "PCM", "NCERT", "NCERT", 8, "A", "3", "2"),
    ("Biology Class 11", "NCERT", "9788174507143", "Biology", "11", "General", "NCERT", "NCERT", 8, "A", "2", "4"),
    ("Biology Class 12", "NCERT", "9788174507242", "Biology", "12", "General", "NCERT", "NCERT", 8, "A", "3", "4"),
    ("Accountancy Class 11", "NCERT", "9788174507341", "Accountancy", "11", "Commerce", "NCERT", "NCERT", 7, "A", "4", "1"),
    ("Business Studies Class 12", "NCERT", "9788174507440", "Business Studies", "12", "Commerce", "NCERT", "NCERT", 7, "A", "4", "2"),
    ("Economics Class 12", "NCERT", "9788174507549", "Economics", "12", "Commerce", "NCERT", "NCERT", 7, "A", "4", "3"),
    ("Macbeth (Drama)", "William Shakespeare", "9780743477109", "English", "11", "Humanities", "Textbook", "Cambridge UP", 5, "B", "1", "1"),
    ("India After Gandhi", "Ramachandra Guha", "9780060198817", "History", "12", "Humanities", "Reference", "HarperCollins", 3, "B", "1", "2"),
    ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "English", "11", "Humanities", "Textbook", "Scribner", 5, "B", "1", "3"),
    ("To Kill a Mockingbird", "Harper Lee", "9780061120084", "English", "9", "General", "Textbook", "HarperCollins", 6, "B", "2", "1"),
    ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "9780062316097", "History", "12", "Humanities", "Reference", "Harper", 3, "B", "2", "2"),
    ("The Theory of Everything", "Stephen Hawking", "9781780227681", "Physics", "12", "PCM", "Reference", "John Murray", 2, "B", "2", "3"),
    ("Organic Chemistry Vol 1", "O.P. Tandon", "9788193655274", "Chemistry", "12", "PCM", "Competition", "G.R. Bathla", 4, "B", "3", "1"),
    ("Problems in General Physics", "I.E. Irodov", "9789350150272", "Physics", "12", "PCM", "Competition", "Shiksha", 3, "B", "3", "2"),
    ("Quantitative Aptitude", "R.S. Aggarwal", "9788173350616", "Mathematics", "10", "General", "Competition", "S. Chand", 5, "B", "4", "1"),
    ("General Knowledge 2024", "Manohar Pandey", "9789350126748", "General Knowledge", "10", "General", "General", "Arihant", 6, "C", "1", "1"),
    ("India Year Book", "Govt of India", "9788123223456", "Current Affairs", "12", "General", "Reference", "GOI Press", 3, "C", "1", "2"),
    ("Moral Science Book 5", "N.K. Sharma", "9788121923456", "Moral Science", "5", "General", "Textbook", "S. Chand", 10, "C", "2", "1"),
    ("Environmental Studies Class 4", "E. Bharucha", "9788179332345", "Environmental Studies", "4", "General", "Textbook", "NCERT", 12, "C", "2", "2"),
    ("Computer Science Class 12", "Sumita Arora", "9788176562346", "Computer Science", "12", "PCM", "Textbook", "Dhanpat Rai", 8, "C", "3", "1"),
    ("Competition Success Review", "—", "", "Current Affairs", "12", "General", "Magazine", "CSR", 4, "D", "1", "1"),
    ("India Today (Monthly)", "—", "", "Current Affairs", "12", "General", "Magazine", "India Today", 3, "D", "1", "2"),
    ("NPGS (Civil Services)", "—", "", "Current Affairs", "12", "General", "Magazine", "NPGS", 2, "D", "1", "3"),
    ("Sanskrit Class 9", "NCERT", "9788174507649", "Sanskrit", "9", "General", "NCERT", "NCERT", 10, "A", "5", "1"),
    ("Political Science Class 11", "NCERT", "9788174507748", "Political Science", "11", "Humanities", "NCERT", "NCERT", 7, "A", "5", "2"),
    ("Geography Class 10", "NCERT", "9788174507847", "Geography", "10", "General", "NCERT", "NCERT", 12, "A", "5", "3"),
    ("Physics - HC Verma Vol 1", "H.C. Verma", "9788177092300", "Physics", "11", "PCM", "Competition", "Bharati Bhawan", 4, "B", "3", "3"),
    ("Concise Mathematics - ICSE 10", "Selina", "9788193923458", "Mathematics", "10", "General", "Textbook", "Selina", 6, "C", "4", "1"),
    ("Hindi - Kshitij Class 10", "NCERT", "9788174507946", "Hindi", "10", "General", "NCERT", "NCERT", 12, "A", "5", "4"),
]

TRANSACTION_TEMPLATES = [
    # (student_index, book_index, days_ago_issue, days_ago_return, status)
    # "issued" -> status="issued", return_date=None
    # "returned" -> status="returned", return_date set
    # "overdue" -> status="issued", issue_date well in past
    # "return_requested" -> status="return_requested"
    (0, 0, 3, None, "issued"),
    (0, 1, 5, None, "issued"),
    (1, 2, 2, None, "issued"),
    (2, 0, 10, None, "overdue"),
    (3, 4, 8, None, "overdue"),
    (4, 6, 1, None, "issued"),
    (5, 5, 12, None, "overdue"),
    (6, 7, 4, None, "issued"),
    (7, 8, 6, None, "issued"),
    (8, 9, 15, None, "overdue"),
    (9, 10, 2, None, "issued"),
    (10, 11, 20, None, "overdue"),
    (11, 12, 3, None, "issued"),
    (12, 13, 7, None, "issued"),
    (13, 14, 14, None, "overdue"),
    # returned ones
    (0, 15, 40, 35, "returned"),
    (1, 16, 38, 30, "returned"),
    (2, 17, 45, 41, "returned"),
    (3, 18, 50, 48, "returned"),
    (4, 19, 60, 55, "returned"),
    (5, 20, 55, 53, "returned"),
    (6, 21, 42, 40, "returned"),
    (7, 22, 35, 33, "returned"),
    (8, 23, 30, 28, "returned"),
    (9, 24, 25, 23, "returned"),
    (10, 25, 20, 18, "returned"),
    # return_requested (pending approval)
    (14, 3, 6, None, "return_requested"),
    (15, 26, 4, None, "return_requested"),
    # some more returned with fines
    (11, 27, 50, 44, "returned"),
    (12, 28, 55, 49, "returned"),
    (13, 29, 48, 42, "returned"),
    (2, 30, 35, 34, "returned"),
    (5, 31, 28, 27, "returned"),
    (7, 32, 22, 21, "returned"),
    (0, 33, 18, 17, "returned"),
    (3, 34, 15, 14, "returned"),
    (6, 35, 12, 11, "returned"),
]

# ── main ─────────────────────────────────────────────────────────────────
def seed():
    db = get_db()
    delete_all(db)

    hashed_pw = generate_password_hash("student123")

    # insert students
    student_ids = []
    for username, email, role in STUDENTS:
        c = db.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            (username, hashed_pw, email, role),
        )
        student_ids.append(c.lastrowid)

    # insert books
    book_ids = []
    for t in BOOKS:
        title, author, isbn, subject, class_level, stream, book_type, publisher, total, sblock, srow, scol = t
        c = db.execute("""
            INSERT INTO books (title, author, isbn, subject, class_level, stream, book_type, publisher, total_copies, available_copies, shelf_block, shelf_row, shelf_column, registered_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now', ?))
        """, (title, author, isbn, subject, class_level, stream, book_type, publisher, total, total, sblock, srow, scol,
              f"-{random.randint(1, 180)} days"))
        book_ids.append(c.lastrowid)

    # insert transactions
    today = datetime.now().date()
    for sidx, bidx, days_ago_issue, days_ago_return, status in TRANSACTION_TEMPLATES:
        uid = student_ids[sidx % len(student_ids)]
        bid = book_ids[bidx % len(book_ids)]

        issue_date = today - timedelta(days=days_ago_issue)
        due_date = issue_date + timedelta(days=7)
        return_date = None
        fine = 0
        actual_status = status

        if status == "overdue":
            actual_status = "issued"
            # overdue but not yet returned
            fine = max(0, (today - due_date).days) * 10
        elif status == "returned":
            rd = today - timedelta(days=days_ago_return) if days_ago_return else today
            return_date = rd
            due = issue_date + timedelta(days=7)
            fine = max(0, (rd - due).days) * 10
            actual_status = "returned"
        elif status == "return_requested":
            fine = max(0, (today - due_date).days) * 10

        txn_id = db.execute("""
            INSERT INTO transactions (user_id, book_id, issue_date, return_date, due_date, fine, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (uid, bid, issue_date.isoformat(),
              return_date.isoformat() if return_date else None,
              due_date.isoformat(), fine, actual_status)).lastrowid

        if status in ("issued", "overdue", "return_requested"):
            db.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id=?", (bid,))

    db.commit()
    db.close()

    print("✅ Database seeded successfully!")
    print(f"   • 1 admin (admin / admin123)")
    print(f"   • {len(STUDENTS)} students (all passwords: student123)")
    print(f"   • {len(BOOKS)} books")
    print(f"   • {len(TRANSACTION_TEMPLATES)} transactions (issued, returned, overdue, pending)")

if __name__ == "__main__":
    seed()
