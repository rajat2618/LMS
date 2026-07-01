from flask import Flask, render_template, request, redirect, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = "library_management_secret_key_2024"

CLASS_LEVELS = ['Nursery', 'KG', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
STREAMS = ['General', 'PCM', 'Commerce', 'Humanities']
BOOK_TYPES = ['Textbook', 'NCERT', 'Magazine', 'Reference', 'Competition', 'General']
SUBJECTS = [
    'Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology',
    'English', 'Hindi', 'Sanskrit', 'Social Studies', 'History',
    'Geography', 'Political Science', 'Economics', 'Accountancy',
    'Business Studies', 'Computer Science', 'Physical Education',
    'Art', 'Music', 'General Knowledge', 'Moral Science',
    'Environmental Studies', 'Current Affairs'
]
MAGAZINE_TYPES = ['NPGS', 'Competition Success Review', 'India Today', 'General']

SUBJECTS_BY_CLASS = {
    'Nursery':   ['Art', 'Music', 'General Knowledge', 'Moral Science', 'English', 'Hindi', 'Environmental Studies', 'Mathematics', 'Current Affairs'],
    'KG':        ['Art', 'Music', 'General Knowledge', 'Moral Science', 'English', 'Hindi', 'Environmental Studies', 'Mathematics', 'Current Affairs'],
    '1':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'Environmental Studies', 'General Knowledge', 'Moral Science', 'Art', 'Music', 'Computer Science'],
    '2':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'Environmental Studies', 'General Knowledge', 'Moral Science', 'Art', 'Music', 'Computer Science'],
    '3':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'Environmental Studies', 'General Knowledge', 'Moral Science', 'Art', 'Music', 'Computer Science'],
    '4':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'Environmental Studies', 'General Knowledge', 'Moral Science', 'Art', 'Music', 'Computer Science'],
    '5':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'Environmental Studies', 'General Knowledge', 'Moral Science', 'Art', 'Music', 'Computer Science'],
    '6':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'History', 'Geography', 'Computer Science', 'Physical Education', 'Art', 'Music', 'Sanskrit', 'General Knowledge'],
    '7':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'History', 'Geography', 'Computer Science', 'Physical Education', 'Art', 'Music', 'Sanskrit', 'General Knowledge'],
    '8':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'History', 'Geography', 'Computer Science', 'Physical Education', 'Art', 'Music', 'Sanskrit', 'General Knowledge'],
    '9':  ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'History', 'Geography', 'Computer Science', 'Physical Education', 'Sanskrit'],
    '10': ['English', 'Hindi', 'Mathematics', 'Science', 'Social Studies', 'History', 'Geography', 'Computer Science', 'Physical Education', 'Sanskrit'],
    '11': ['English', 'Hindi', 'Sanskrit', 'Computer Science', 'Physical Education', 'Physics', 'Chemistry', 'Biology', 'Mathematics', 'History', 'Geography', 'Political Science', 'Economics', 'Accountancy', 'Business Studies'],
    '12': ['English', 'Hindi', 'Sanskrit', 'Computer Science', 'Physical Education', 'Physics', 'Chemistry', 'Biology', 'Mathematics', 'History', 'Geography', 'Political Science', 'Economics', 'Accountancy', 'Business Studies'],
}

def get_db():
    db = sqlite3.connect("library.db")
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT,
        subject TEXT DEFAULT 'General',
        class_level TEXT DEFAULT 'General',
        stream TEXT DEFAULT 'General',
        book_type TEXT DEFAULT 'Textbook',
        magazine_name TEXT,
        publisher TEXT,
        total_copies INTEGER DEFAULT 1,
        available_copies INTEGER DEFAULT 1,
        shelf_row TEXT,
        shelf_column TEXT,
        shelf_block TEXT,
        registered_date TEXT DEFAULT (date('now')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    for col in ['shelf_row', 'shelf_column', 'shelf_block', 'registered_date']:
        try:
            cursor.execute(f"ALTER TABLE books ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        issue_date TEXT NOT NULL,
        return_date TEXT,
        due_date TEXT NOT NULL,
        fine INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'issued',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    )
    """)

    cursor.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cursor.fetchone():
        hashed_password = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
            ("admin", hashed_password, "admin", "admin@library.com")
        )

    db.commit()
    db.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_globals():
    return {
        'now': datetime.now().strftime("%Y-%m-%d"),
        'CLASS_LEVELS': CLASS_LEVELS,
        'STREAMS': STREAMS,
        'BOOK_TYPES': BOOK_TYPES,
        'SUBJECTS': SUBJECTS,
        'MAGAZINE_TYPES': MAGAZINE_TYPES,
        'SUBJECTS_BY_CLASS': SUBJECTS_BY_CLASS
    }

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error='Username and password required')

        db = get_db()
        user = db.execute(
            "SELECT id, username, password, role FROM users WHERE username=?",
            (username,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect('/admin' if user['role'] == 'admin' else '/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        email = request.form.get('email', '').strip()

        if not username or not password or not email:
            return render_template('register.html', error='All fields are required')
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        db = get_db()
        try:
            hashed_password = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, 'student')",
                (username, hashed_password, email)
            )
            db.commit()
            db.close()
            return render_template('register.html', success='Registration successful! Please login.')
        except sqlite3.IntegrityError:
            db.close()
            return render_template('register.html', error='Username already exists')

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()

    subject = request.args.get('subject', '').strip()
    class_level = request.args.get('class_level', '').strip()
    book_type = request.args.get('book_type', '').strip()

    query = "SELECT * FROM books WHERE 1=1"
    params = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if class_level:
        query += " AND class_level = ?"
        params.append(class_level)
    if book_type:
        query += " AND book_type = ?"
        params.append(book_type)
    query += " ORDER BY title"

    books = db.execute(query, params).fetchall()

    user_transactions = db.execute("""
        SELECT t.*, b.title, b.author, b.subject, b.class_level, b.book_type
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.user_id = ?
        ORDER BY t.issue_date DESC
    """, (session['user_id'],)).fetchall()

    today = datetime.now().date()
    overdue_count = 0
    due_soon_count = 0
    txn_list = []
    for txn in user_transactions:
        d = dict(txn)
        if d['status'] == 'issued' and d['due_date']:
            due = datetime.strptime(d['due_date'], "%Y-%m-%d").date()
            d['is_overdue'] = today > due
            d['due_soon'] = not d['is_overdue'] and 0 <= (due - today).days <= 2
            if d['is_overdue']:
                overdue_count += 1
            elif d['due_soon']:
                due_soon_count += 1
        else:
            d['is_overdue'] = False
            d['due_soon'] = False
        txn_list.append(d)

    db.close()

    return render_template('dashboard.html',
                         books=books,
                         transactions=txn_list,
                         overdue_count=overdue_count,
                         due_soon_count=due_soon_count,
                         filters={'subject': subject, 'class_level': class_level, 'book_type': book_type})

@app.route('/issue/<int:book_id>')
@login_required
@admin_required
def issue_book(book_id):
    student_id = request.args.get('student_id', type=int)
    if not student_id:
        return redirect('/manage-books')

    db = get_db()
    student = db.execute(
        "SELECT id FROM users WHERE id=? AND role='student'", (student_id,)
    ).fetchone()

    book = db.execute(
        "SELECT available_copies FROM books WHERE id=?", (book_id,)
    ).fetchone()

    if not student or not book or book['available_copies'] <= 0:
        db.close()
        return redirect('/manage-books')

    already_issued = db.execute("""
        SELECT id FROM transactions
        WHERE user_id=? AND book_id=? AND status='issued'
    """, (student_id, book_id)).fetchone()
    if already_issued:
        db.close()
        return redirect('/manage-books')

    issue_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    db.execute(
        "INSERT INTO transactions (user_id, book_id, issue_date, due_date, status) VALUES (?, ?, ?, ?, 'issued')",
        (student_id, book_id, issue_date, due_date)
    )
    db.execute(
        "UPDATE books SET available_copies = available_copies - 1 WHERE id=?",
        (book_id,)
    )
    db.commit()
    db.close()
    return redirect('/manage-books')

@app.route('/return/<int:transaction_id>')
@login_required
@admin_required
def return_book(transaction_id):
    db = get_db()
    txn = db.execute(
        "SELECT * FROM transactions WHERE id=?", (transaction_id,)
    ).fetchone()

    if not txn or txn['status'] != 'issued':
        db.close()
        return redirect('/manage-books')

    today = datetime.now()
    due_date = datetime.strptime(txn['due_date'], "%Y-%m-%d")
    fine = max(0, (today - due_date).days * 10) if today > due_date else 0

    db.execute(
        "UPDATE transactions SET fine=?, status='return_requested' WHERE id=?",
        (fine, transaction_id)
    )
    db.commit()
    db.close()
    return redirect('/manage-books')

@app.route('/confirm-return/<int:transaction_id>')
@login_required
@admin_required
def confirm_return(transaction_id):
    db = get_db()
    txn = db.execute(
        "SELECT * FROM transactions WHERE id=?", (transaction_id,)
    ).fetchone()

    if not txn or txn['status'] != 'return_requested':
        db.close()
        return redirect('/transactions')

    return_date = datetime.now().strftime("%Y-%m-%d")
    db.execute(
        "UPDATE transactions SET return_date=?, status='returned' WHERE id=?",
        (return_date, transaction_id)
    )
    db.execute(
        "UPDATE books SET available_copies = available_copies + 1 WHERE id=?",
        (txn['book_id'],)
    )
    db.commit()
    db.close()
    return redirect('/transactions')

@app.route('/reject-return/<int:transaction_id>')
@login_required
@admin_required
def reject_return(transaction_id):
    db = get_db()
    txn = db.execute(
        "SELECT * FROM transactions WHERE id=?", (transaction_id,)
    ).fetchone()
    if not txn or txn['status'] != 'return_requested':
        db.close()
        return redirect('/transactions')
    db.execute("UPDATE transactions SET status='issued' WHERE id=?", (transaction_id,))
    db.commit()
    db.close()
    return redirect('/transactions')

@app.route('/manage-books')
@login_required
@admin_required
def manage_books():
    db = get_db()

    students = db.execute(
        "SELECT id, username, email FROM users WHERE role='student' ORDER BY username"
    ).fetchall()

    available_books = db.execute("""
        SELECT id, title, author, subject, class_level, stream, book_type, available_copies
        FROM books WHERE available_copies > 0 ORDER BY title
    """).fetchall()

    issued_rows = db.execute("""
        SELECT t.id, u.username, b.title, t.issue_date, t.due_date, t.fine, t.status,
               b.subject, b.class_level
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN books b ON t.book_id = b.id
        WHERE t.status IN ('issued', 'return_requested')
        ORDER BY t.issue_date DESC
    """).fetchall()

    db.close()

    today = datetime.now().date()
    issued_books = []
    for row in issued_rows:
        d = dict(row)
        if d['due_date']:
            due = datetime.strptime(d['due_date'], "%Y-%m-%d").date()
            d['is_overdue'] = today > due
            d['due_soon'] = not d['is_overdue'] and 0 <= (due - today).days <= 2
        else:
            d['is_overdue'] = False
            d['due_soon'] = False
        issued_books.append(d)

    return render_template('manage_books.html',
                         students=students,
                         available_books=available_books,
                         issued_books=issued_books)

@app.route('/admin')
@login_required
@admin_required
def admin():
    db = get_db()
    search = request.args.get('search', '').strip()
    subject = request.args.get('subject', '').strip()
    class_level = request.args.get('class_level', '').strip()
    book_type = request.args.get('book_type', '').strip()

    query = "SELECT * FROM books WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if class_level:
        query += " AND class_level = ?"
        params.append(class_level)
    if book_type:
        query += " AND book_type = ?"
        params.append(book_type)
    query += " ORDER BY title"

    books = db.execute(query, params).fetchall()

    total_books = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    issued_books = db.execute("SELECT COUNT(*) FROM transactions WHERE status='issued'").fetchone()[0]
    return_requested = db.execute("SELECT COUNT(*) FROM transactions WHERE status='return_requested'").fetchone()[0]
    returned_books = db.execute("SELECT COUNT(*) FROM transactions WHERE status='returned'").fetchone()[0]
    total_fine = db.execute("SELECT COALESCE(SUM(fine), 0) FROM transactions").fetchone()[0]
    total_users = db.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]
    overdue_books = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE status='issued' AND due_date < date('now')"
    ).fetchone()[0]
    due_today = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE status='issued' AND due_date = date('now')"
    ).fetchone()[0]
    due_tomorrow = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE status='issued' AND due_date = date('now', '+1 day')"
    ).fetchone()[0]

    db.close()

    return render_template('admin.html',
                         stats={
                             'total_books': total_books,
                             'issued_books': issued_books,
                             'return_requested': return_requested,
                             'returned_books': returned_books,
                             'total_fine': total_fine,
                             'total_users': total_users,
                             'overdue_books': overdue_books,
                             'due_today': due_today,
                             'due_tomorrow': due_tomorrow
                         },
                         books=books,
                         search=search,
                         filters={'subject': subject, 'class_level': class_level, 'book_type': book_type})

@app.route('/add-book', methods=['POST'])
@login_required
@admin_required
def add_book():
    db = get_db()
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    isbn = request.form.get('isbn', '').strip()
    subject = request.form.get('subject', 'General').strip()
    class_level = request.form.get('class_level', 'General').strip()
    stream = request.form.get('stream', 'General').strip()
    book_type = request.form.get('book_type', 'Textbook').strip()
    magazine_name = request.form.get('magazine_name', '').strip()
    publisher = request.form.get('publisher', '').strip()
    copies = int(request.form.get('copies', 1))
    shelf_row = request.form.get('shelf_row', '').strip().upper()
    shelf_column = request.form.get('shelf_column', '').strip().upper()
    shelf_block = request.form.get('shelf_block', '').strip().upper()

    if not title or not author:
        flash('Title and Author are required.', 'error')
        db.close()
        return redirect('/admin')

    title = ' '.join(w.capitalize() for w in title.split())
    author = ' '.join(w.capitalize() for w in author.split())
    publisher = ' '.join(w.capitalize() for w in publisher.split()) if publisher else ''
    isbn = isbn.replace('-', '').replace(' ', '')

    db.execute("""
        INSERT INTO books (title, author, isbn, subject, class_level, stream, book_type, magazine_name, publisher, total_copies, available_copies, shelf_row, shelf_column, shelf_block, registered_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
    """, (title, author, isbn, subject, class_level, stream, book_type, magazine_name, publisher, copies, copies, shelf_row, shelf_column, shelf_block))

    db.commit()
    db.close()
    flash(f'Book "{title}" added successfully!', 'success')
    return redirect('/admin')

@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    db = get_db()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        subject = request.form.get('subject', 'General').strip()
        class_level = request.form.get('class_level', 'General').strip()
        stream = request.form.get('stream', 'General').strip()
        book_type = request.form.get('book_type', 'Textbook').strip()
        magazine_name = request.form.get('magazine_name', '').strip()
        publisher = request.form.get('publisher', '').strip()
        shelf_row = request.form.get('shelf_row', '').strip().upper()
        shelf_column = request.form.get('shelf_column', '').strip().upper()
        shelf_block = request.form.get('shelf_block', '').strip().upper()

        if title and author:
            title = ' '.join(w.capitalize() for w in title.split())
            author = ' '.join(w.capitalize() for w in author.split())
            publisher = ' '.join(w.capitalize() for w in publisher.split()) if publisher else ''
            isbn = isbn.replace('-', '').replace(' ', '')
            db.execute("""
                UPDATE books SET title=?, author=?, isbn=?, subject=?, class_level=?,
                stream=?, book_type=?, magazine_name=?, publisher=?,
                shelf_row=?, shelf_column=?, shelf_block=? WHERE id=?
            """, (title, author, isbn, subject, class_level, stream, book_type, magazine_name, publisher, shelf_row, shelf_column, shelf_block, book_id))
            db.commit()
            flash(f'Book "{title}" updated successfully!', 'success')
        db.close()
        return redirect('/admin')

    book = db.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    db.close()
    if not book:
        return redirect('/admin')
    return render_template('edit_book.html', book=book)

@app.route('/delete-book/<int:book_id>')
@login_required
@admin_required
def delete_book(book_id):
    db = get_db()
    issued = db.execute(
        "SELECT id FROM transactions WHERE book_id=? AND status='issued'", (book_id,)
    ).fetchone()
    if issued:
        db.close()
        return redirect('/admin')
    db.execute("DELETE FROM books WHERE id=?", (book_id,))
    db.commit()
    db.close()
    return redirect('/admin')

@app.route('/users')
@login_required
@admin_required
def view_users():
    db = get_db()
    search = request.args.get('search', '').strip()

    if search:
        users = db.execute(
            "SELECT id, username, email, role, created_at FROM users WHERE username LIKE ? OR email LIKE ? ORDER BY created_at DESC",
            (f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        users = db.execute(
            "SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
    db.close()
    return render_template('users.html', users=users, search=search)

@app.route('/delete-user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    db = get_db()
    user = db.execute("SELECT role FROM users WHERE id=?", (user_id,)).fetchone()
    if not user or user['role'] == 'admin' or user_id == session['user_id']:
        db.close()
        return redirect('/users')
    db.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    db.close()
    return redirect('/users')

@app.route('/change-role/<int:user_id>/<role>')
@login_required
@admin_required
def change_role(user_id, role):
    if role not in ['admin', 'student'] or user_id == session['user_id']:
        return redirect('/users')
    db = get_db()
    db.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    db.commit()
    db.close()
    return redirect('/users')

@app.route('/transactions')
@login_required
@admin_required
def view_transactions():
    db = get_db()

    status_filter = request.args.get('status', '').strip()
    query = """
        SELECT t.id, u.username, b.title, t.issue_date, t.return_date,
               t.due_date, t.fine, t.status, b.subject, b.class_level, b.book_type
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN books b ON t.book_id = b.id
    """
    params = []
    if status_filter:
        query += " WHERE t.status = ?"
        params.append(status_filter)
    query += " ORDER BY t.issue_date DESC"

    transactions = db.execute(query, params).fetchall()
    db.close()

    return render_template('transactions.html', transactions=transactions, status_filter=status_filter)

@app.route('/api/chart-data')
@login_required
@admin_required
def get_chart_data():
    db = get_db()

    books_data = db.execute("SELECT subject, COUNT(*) as count FROM books GROUP BY subject ORDER BY count DESC LIMIT 8").fetchall()
    status_data = db.execute("SELECT status, COUNT(*) as count FROM transactions GROUP BY status").fetchall()
    fine_data = db.execute("""
        SELECT strftime('%Y-%m', issue_date) as month, SUM(fine) as total
        FROM transactions GROUP BY strftime('%Y-%m', issue_date)
        ORDER BY month DESC LIMIT 12
    """).fetchall()

    db.close()

    return jsonify({
        'books': [{'title': b['subject'], 'count': b['count']} for b in books_data],
        'status': [{'name': s['status'], 'count': s['count']} for s in status_data],
        'fines': [{'month': f['month'], 'amount': f['total'] or 0} for f in fine_data]
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
