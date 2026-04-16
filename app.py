from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = "library_management_secret_key_2024"

# ========== DATABASE CONNECTION ==========
def get_db():
    """Get database connection"""
    db = sqlite3.connect("library.db")
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize database with tables"""
    db = get_db()
    cursor = db.cursor()

    # Users table
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

    # Books table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT,
        total_copies INTEGER DEFAULT 1,
        available_copies INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        issue_date TEXT NOT NULL,
        return_date TEXT,
        due_date TEXT,
        fine INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'issued',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    )
    """)

    # Insert default admin user
    cursor.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cursor.fetchone():
        hashed_password = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
            ("admin", hashed_password, "admin", "admin@library.com")
        )

    db.commit()
    db.close()


# Initialize database on startup
init_db()


# ========== DECORATORS ==========
def login_required(f):
    """Check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function


# ========== LOGIN & REGISTER ==========
@app.route('/', methods=['GET', 'POST'])
def login():
    """Login page"""
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

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]

            if user[3] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        email = request.form.get('email', '').strip()

        # Validation
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


# ========== STUDENT DASHBOARD ==========
@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard - view books and transactions"""
    db = get_db()

    # Get all books with availability
    books = db.execute("""
        SELECT id, title, author, total_copies, available_copies, isbn 
        FROM books 
        ORDER BY title
    """).fetchall()

    # Get user's transactions
    user_transactions = db.execute("""
        SELECT t.id, b.title, b.author, t.issue_date, t.return_date, 
               t.due_date, t.fine, t.status, b.id as book_id
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.user_id = ?
        ORDER BY t.issue_date DESC
    """, (session['user_id'],)).fetchall()

    # Calculate overdue books
    overdue_count = 0
    for txn in user_transactions:
        if txn[7] == 'issued' and txn[5]:  # status = 'issued' and due_date exists
            due_date = datetime.strptime(txn[5], "%Y-%m-%d")
            if datetime.now() > due_date:
                overdue_count += 1

    db.close()

    return render_template('dashboard.html', 
                         books=books, 
                         transactions=user_transactions,
                         overdue_count=overdue_count)


# ========== BOOK OPERATIONS ==========
@app.route('/issue/<int:book_id>')
@login_required
@admin_required
def issue_book(book_id):
    """Issue a book to a student (LIBRARIAN ONLY)"""
    student_id = request.args.get('student_id', type=int)
    
    if not student_id:
        return redirect('/manage-books')

    db = get_db()

    # Check if student exists
    student = db.execute(
        "SELECT id FROM users WHERE id=? AND role='student'",
        (student_id,)
    ).fetchone()

    if not student:
        db.close()
        return redirect('/manage-books')

    # Check if book exists and has copies
    book = db.execute(
        "SELECT available_copies FROM books WHERE id=?",
        (book_id,)
    ).fetchone()

    if not book or book[0] <= 0:
        db.close()
        return redirect('/manage-books')

    # Check if already issued to this student
    already_issued = db.execute("""
        SELECT * FROM transactions 
        WHERE user_id=? AND book_id=? AND status='issued'
    """, (student_id, book_id)).fetchone()

    if already_issued:
        db.close()
        return redirect('/manage-books')

    # Issue book (due date = 14 days from now)
    issue_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    db.execute("""
        INSERT INTO transactions (user_id, book_id, issue_date, due_date, status)
        VALUES (?, ?, ?, ?, 'issued')
    """, (student_id, book_id, issue_date, due_date))

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
    """Request to return a book - librarian marks as pending when student brings it"""
    db = get_db()

    # Get transaction details
    txn = db.execute("""
        SELECT id, user_id, book_id, issue_date, due_date, status 
        FROM transactions 
        WHERE id=?
    """, (transaction_id,)).fetchone()

    if not txn or txn[5] != 'issued':
        db.close()
        return redirect('/manage-books')

    # Calculate fine based on due date
    today = datetime.now()
    due_date = datetime.strptime(txn[4], "%Y-%m-%d") if txn[4] else today
    
    if today > due_date:
        days_late = (today - due_date).days
        fine = days_late * 5  # ₹5 per day fine
    else:
        fine = 0

    # Update transaction status to 'return_requested' (student brought book)
    db.execute("""
        UPDATE transactions 
        SET fine=?, status='return_requested'
        WHERE id=?
    """, (fine, transaction_id))

    db.commit()
    db.close()

    return redirect('/manage-books')


@app.route('/confirm-return/<int:transaction_id>')
@login_required
@admin_required
def confirm_return(transaction_id):
    """Librarian confirms book return (after physically receiving it)"""
    db = get_db()

    # Get transaction details
    txn = db.execute("""
        SELECT id, user_id, book_id, issue_date, due_date, status, fine
        FROM transactions 
        WHERE id=?
    """, (transaction_id,)).fetchone()

    if not txn or txn[5] != 'return_requested':
        db.close()
        return redirect('/transactions')

    # Set return date and mark as returned
    return_date = datetime.now().strftime("%Y-%m-%d")
    db.execute("""
        UPDATE transactions 
        SET return_date=?, status='returned'
        WHERE id=?
    """, (return_date, transaction_id))

    # Update book availability - add back one copy
    db.execute(
        "UPDATE books SET available_copies = available_copies + 1 WHERE id=?",
        (txn[2],)
    )

    db.commit()
    db.close()

    return redirect('/transactions')


@app.route('/reject-return/<int:transaction_id>')
@login_required
@admin_required
def reject_return(transaction_id):
    """Librarian rejects book return request (user not returning properly)"""
    db = get_db()

    # Get transaction details
    txn = db.execute("""
        SELECT id, status
        FROM transactions 
        WHERE id=?
    """, (transaction_id,)).fetchone()

    if not txn or txn[1] != 'return_requested':
        db.close()
        return redirect('/transactions')

    # Revert status back to issued
    db.execute("""
        UPDATE transactions 
        SET status='issued'
        WHERE id=?
    """, (transaction_id,))

    db.commit()
    db.close()

    return redirect('/transactions')


# ========== BOOK MANAGEMENT PAGE (LIBRARIAN) ==========
@app.route('/manage-books')
@login_required
@admin_required
def manage_books():
    """Librarian page to issue books to students and manage returns"""
    db = get_db()
    
    # Get all students
    students = db.execute("""
        SELECT id, username, email FROM users WHERE role='student' ORDER BY username
    """).fetchall()
    
    # Get all available books
    available_books = db.execute("""
        SELECT id, title, author, available_copies, isbn FROM books 
        WHERE available_copies > 0 ORDER BY title
    """).fetchall()
    
    # Get all issued books with student info
    issued_books = db.execute("""
        SELECT t.id, u.username, b.title, t.issue_date, t.due_date, t.fine, t.status
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN books b ON t.book_id = b.id
        WHERE t.status IN ('issued', 'return_requested')
        ORDER BY t.issue_date DESC
    """).fetchall()
    
    db.close()
    
    return render_template('manage_books.html', 
                         students=students,
                         available_books=available_books,
                         issued_books=issued_books)


# ========== ADMIN PANEL ==========
@app.route('/admin')
@login_required
@admin_required
def admin():
    """Admin dashboard"""
    db = get_db()
    search_query = request.args.get('search', '').strip()

    # Get books
    if search_query:
        books = db.execute("""
            SELECT id, title, author, total_copies, available_copies, isbn 
            FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
            ORDER BY title
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")).fetchall()
    else:
        books = db.execute("""
            SELECT id, title, author, total_copies, available_copies, isbn 
            FROM books 
            ORDER BY title
        """).fetchall()

    # Calculate statistics
    total_books = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    issued_books = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE status='issued'"
    ).fetchone()[0]
    return_requested = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE status='return_requested'"
    ).fetchone()[0]
    returned_books = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE status='returned'"
    ).fetchone()[0]
    total_fine = db.execute(
        "SELECT COALESCE(SUM(fine), 0) FROM transactions"
    ).fetchone()[0]
    total_users = db.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]

    # Overdue books
    overdue_books = db.execute("""
        SELECT COUNT(*) FROM transactions 
        WHERE status='issued' AND due_date < date('now')
    """).fetchone()[0]

    stats = {
        'total_books': total_books,
        'issued_books': issued_books,
        'return_requested': return_requested,
        'returned_books': returned_books,
        'total_fine': total_fine,
        'total_users': total_users,
        'overdue_books': overdue_books
    }

    db.close()

    return render_template('admin.html', stats=stats, books=books, search=search_query)


# ========== BOOK MANAGEMENT ==========
@app.route('/add-book', methods=['POST'])
@login_required
@admin_required
def add_book():
    """Add new book"""
    db = get_db()
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    isbn = request.form.get('isbn', '').strip()
    copies = int(request.form.get('copies', 1))

    if not title or not author:
        db.close()
        return redirect('/admin')

    db.execute("""
        INSERT INTO books (title, author, isbn, total_copies, available_copies)
        VALUES (?, ?, ?, ?, ?)
    """, (title, author, isbn, copies, copies))

    db.commit()
    db.close()

    return redirect('/admin')


@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    """Edit book details"""
    db = get_db()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()

        if title and author:
            db.execute("""
                UPDATE books 
                SET title=?, author=?, isbn=?
                WHERE id=?
            """, (title, author, isbn, book_id))
            db.commit()

        db.close()
        return redirect('/admin')

    # GET - show edit form
    book = db.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    db.close()

    if not book:
        return redirect('/admin')

    return render_template('edit_book.html', book=book)


@app.route('/delete-book/<int:book_id>')
@login_required
@admin_required
def delete_book(book_id):
    """Delete book (only if not issued)"""
    db = get_db()

    # Check if book is issued
    issued = db.execute("""
        SELECT * FROM transactions WHERE book_id=? AND status='issued'
    """, (book_id,)).fetchone()

    if issued:
        # Cannot delete - book is issued
        db.close()
        return redirect('/admin')

    db.execute("DELETE FROM books WHERE id=?", (book_id,))
    db.commit()
    db.close()

    return redirect('/admin')


# ========== USER MANAGEMENT ==========
@app.route('/users')
@login_required
@admin_required
def view_users():
    """View all users"""
    db = get_db()
    search_query = request.args.get('search', '').strip()

    if search_query:
        users = db.execute("""
            SELECT id, username, email, role, created_at 
            FROM users 
            WHERE username LIKE ? OR email LIKE ?
            ORDER BY created_at DESC
        """, (f"%{search_query}%", f"%{search_query}%")).fetchall()
    else:
        users = db.execute("""
            SELECT id, username, email, role, created_at 
            FROM users 
            ORDER BY created_at DESC
        """).fetchall()

    db.close()

    return render_template('users.html', users=users, search=search_query)


@app.route('/delete-user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    """Delete user (only admins can delete)"""
    db = get_db()

    # Prevent deleting admin or self
    user = db.execute("SELECT role FROM users WHERE id=?", (user_id,)).fetchone()

    if not user or user[0] == 'admin' or user_id == session['user_id']:
        db.close()
        return redirect('/users')

    # Delete user's transactions first
    db.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))

    # Delete user
    db.execute("DELETE FROM users WHERE id=?", (user_id,))

    db.commit()
    db.close()

    return redirect('/users')


@app.route('/change-role/<int:user_id>/<role>')
@login_required
@admin_required
def change_role(user_id, role):
    """Change user role"""
    if role not in ['admin', 'student']:
        return redirect('/users')

    # Prevent changing own role
    if user_id == session['user_id']:
        return redirect('/users')

    db = get_db()
    db.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    db.commit()
    db.close()

    return redirect('/users')


# ========== TRANSACTIONS PAGE ==========
@app.route('/transactions')
@login_required
@admin_required
def view_transactions():
    """View all transactions"""
    db = get_db()

    transactions = db.execute("""
        SELECT t.id, u.username, b.title, t.issue_date, t.return_date, 
               t.due_date, t.fine, t.status
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN books b ON t.book_id = b.id
        ORDER BY t.issue_date DESC
    """).fetchall()

    db.close()

    return render_template('transactions.html', transactions=transactions)


# ========== ANALYTICS DATA (for charts) ==========
@app.route('/api/chart-data')
@login_required
@admin_required
def get_chart_data():
    """Get data for charts"""
    db = get_db()

    # Books distribution
    books_data = db.execute("""
        SELECT title, total_copies FROM books LIMIT 5
    """).fetchall()

    # Status distribution
    status_data = db.execute("""
        SELECT status, COUNT(*) FROM transactions GROUP BY status
    """).fetchall()

    # Monthly fine data
    fine_data = db.execute("""
        SELECT strftime('%Y-%m', issue_date) as month, SUM(fine) 
        FROM transactions 
        GROUP BY strftime('%Y-%m', issue_date)
        ORDER BY month DESC
        LIMIT 12
    """).fetchall()

    db.close()

    return jsonify({
        'books': [{'title': b[0], 'count': b[1]} for b in books_data],
        'status': [{'name': s[0], 'count': s[1]} for s in status_data],
        'fines': [{'month': f[0], 'amount': f[1] or 0} for f in fine_data]
    })


# ========== LOGOUT ==========
@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')


# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)