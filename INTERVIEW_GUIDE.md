# Interview Guide — Harrow School Library Management System

## 1. Project Overview (30-sec pitch)

> A **school library management system** built with **Python Flask + SQLite**. Handles book cataloging, issue/return with fine calculation, and admin analytics — all with a premium responsive UI. Designed to replace paper-based school library registers.

---

## 2. Tech Stack & Why

| Layer | Tech | Why |
|-------|------|-----|
| Backend | Python Flask | Lightweight, rapid prototyping, huge ecosystem |
| Database | SQLite | Zero-config, file-based, perfect for school deployment |
| Auth | Werkzeug | Industry-standard password hashing (PBKDF2) |
| Frontend | HTML/CSS/JS + Chart.js | No build step needed, Chart.js for interactive dashboards |
| Template | Jinja2 (Flask built-in) | Server-side rendering, no SPA complexity needed |

---

## 3. Database Schema (3 tables)

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| username | TEXT UNIQUE | Login credential |
| password | TEXT | Hashed with `generate_password_hash` |
| role | TEXT | `admin` or `student` |
| email | TEXT | Validated on register |
| created_at | TIMESTAMP | Auto-set |

### `books`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| title, author, isbn | TEXT | Core metadata |
| subject, class_level, stream, book_type | TEXT | Categorization system |
| magazine_name | TEXT | Only for Magazine type |
| publisher | TEXT | |
| total_copies, available_copies | INTEGER | Tracks inventory |
| shelf_block, shelf_row, shelf_column | TEXT | Physical location in library |
| registered_date | TEXT | Date book was added |

### `transactions`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | FK → users | Who borrowed |
| book_id | FK → books | Which book |
| issue_date | TEXT | Start date |
| due_date | TEXT | issue_date + 7 days |
| return_date | TEXT | Null until returned |
| fine | INTEGER | ₹10/day overdue |
| status | TEXT | `issued` → `return_requested` → `returned` |

---

## 4. Key Architecture Decisions

### Authentication & Authorization
- **`@login_required`** decorator checks `session['user_id']`
- **`@admin_required`** decorator checks `session['role'] == 'admin'`
- Sessions store `user_id`, `username`, `role` (never password)
- Passwords hashed via `werkzeug.security` before storage

### Issue/Return Flow (3-step)
1. Admin selects student + book on `/manage-books` → **Issued** (available_copies -1)
2. Student returns → admin clicks "Mark Return" → status becomes **return_requested**, fine calculated
3. Admin reviews and clicks "Confirm Return" → status **returned**, available_copies +1

Fine formula: `max(0, (today - due_date).days) * 10`

### Fine = ₹10/day overdue, issue period = 7 days

### Role-Based Access
| Route | Student | Admin |
|-------|---------|-------|
| `/dashboard` | Browse books, view transactions | — |
| `/admin` | Redirected to dashboard | Full stats, charts |
| `/manage-books` | — | Issue/return workflow |
| `/transactions` | — | All history |
| `/users` | — | User management |
| `/issue/<id>` | — | Issue a book |
| `/return/<id>` | — | Initiate return |
| `/add-book` | — | Add new book |

### Chart.js Analytics (Admin Dashboard)
- **Bar chart**: Books grouped by subject
- **Doughnut chart**: Issued vs Returned vs Pending
- **Line chart**: Monthly fine collection
- **Stats cards**: Total books, issued, returned, fines, overdue, students

---

## 5. Routing Map

```
/                   → Login (GET/POST)
/register           → Register (GET/POST)
/logout             → Clear session
/dashboard          → Student dashboard (browse books + my transactions)
/admin              → Admin dashboard (stats + book mgmt + charts)
/manage-books       → Issue/Return workflow
/add-book           → POST: add a book
/edit-book/<id>     → GET/POST: edit book details
/delete-book/<id>   → Delete book (fails if issued)
/issue/<id>         → Issue book to student
/return/<id>        → Mark return requested
/confirm-return/<id> → Confirm return
/reject-return/<id> → Reject return request
/users              → User management
/delete-user/<id>   → Delete student user
/change-role        → Promote/demote user
/transactions       → All transactions (with status filter)
/api/chart-data     → JSON endpoint for Chart.js
```

---

## 6. Security Features to Highlight

1. **Password hashing** — No plaintext storage, uses PBKDF2
2. **Parameterized queries** — All SQL uses `?` placeholders (no SQL injection)
3. **Session-based auth** — Server-side session, not token-based (simple for school LAN)
4. **Role decorators** — Routes protected at function level, not just UI hiding
5. **Safety checks** — Can't delete issued books, can't issue unavailable books, can't issue same book twice to same student

---

## 7. UI/UX Features

- **Responsive**: Sidebar collapses to hamburger on mobile
- **Color-coded badges**: Green (returned), Red (issued/danger), Orange (pending/warning)
- **Overdue alerts**: Red banner on dashboard for overdue, yellow for due within 2 days
- **Due date alerts**: Admin dashboard shows due-today and due-tomorrow counts
- **Empty states**: Graceful "No data" messages instead of blank pages
- **Shelf location tracking**: Block/Row/Column system for physical library navigation
- **Class-aware subject filtering**: When you select a class, subjects dropdown updates dynamically

---

## 8. Quick Demo Walkthrough

### Open the app
```bash
source venv/bin/activate && python app.py
# → http://localhost:5000
```

### Admin Login
- **Username:** `admin` / **Password:** `admin123`
- See dashboard with **live stats and 3 charts**
- Go to **Issue & Returns** → select a student + book → issue
- See **pending returns** tab with calculated fines

### Student Login
- Any student account, password: `student123`
- Browse books with subject/class/type filters
- See "My Transaction History" with overdue and due-soon badges

### Show off
- **Dashboard**: Stats cards (totals update in real time), 3 Chart.js graphs
- **User management**: Search, promote/demote, delete users
- **Transactions**: Filter by status, see fine amounts
- **Add book form**: Full classification system (subject, class, stream, type, shelf location)

---

## 9. Common Interview Questions

**Q: Why Flask and not Django?**
A: For a school library system, Flask is lighter, has less boilerplate, and gives more control. SQLite with Flask is a common combo for LAN-deployed school software.

**Q: How does the fine system work?**
A: Fine = `max(0, days_overdue) * 10`. Calculated when admin initiates return. The formula is in the "Mark Return" button handler.

**Q: What if two students try to issue the last copy?**
A: The code checks `available_copies > 0` before issuing, and has an additional check preventing duplicate issue of the same book to the same student. SQL transactions handle concurrency.

**Q: How is the data persistent?**
A: SQLite saves to `library.db` file. No separate database server needed. To reset, just delete the file.

**Q: Can students return books themselves?**
A: In this version, only admins can initiate returns. This adds an oversight layer — admin checks the book condition before confirming.

**Q: How is the shelf tracking useful?**
A: Each book has a shelf location (Block/Row/Column). This mirrors real-world school libraries where books are organized by section (e.g., Block A = NCERT textbooks, Block B = reference).

---

## 10. Potential Improvements (if asked)

- CSV/Excel export for reports
- Barcode/QR code scanning for check-in/check-out
- Email notifications for due dates
- Student self-service return at kiosk
- Book reservation/hold system
- Multi-language support
- Docker containerization for deployment
