# 📚 Library Management System - Production Ready

## 🎯 Project Overview

A complete **school library management system** built with **Python Flask** and **SQLite**. This is a production-level application with premium UI, robust security, and all essential features for managing a school library.

---

## 📂 Project Structure

```
Liabrary harrow/
├── app.py                          # Main Flask application
├── library.db                      # SQLite database (auto-created)
├── requirements.txt                # Python dependencies
├── static/
│   └── style.css                   # Premium responsive CSS
└── templates/
    ├── layout.html                 # Base template for all pages
    ├── login.html                  # Login page
    ├── register.html               # User registration
    ├── dashboard.html              # Student dashboard
    ├── admin.html                  # Admin dashboard with charts
    ├── users.html                  # User management
    ├── edit_book.html              # Edit book details
    ├── transactions.html           # View all transactions
    ├── 404.html                    # Error page
    └── 500.html                    # Server error page
```

---

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
pip install flask werkzeug
```

### 2. **Run the Application**

```bash
python app.py
```

The application will start at: **http://localhost:5000**

### 3. **Default Login Credentials**

```
Username: admin
Password: admin123
```

---

## ✨ Key Features

### 🔐 **Security**
- ✅ Password hashing using `werkzeug.security`
- ✅ Session-based authentication
- ✅ Role-based access control (Admin/Student)
- ✅ Protected routes with decorators
- ✅ CSRF token support ready

### 📚 **Book Management**
- ✅ Add, edit, and delete books
- ✅ Track total and available copies
- ✅ ISBN tracking
- ✅ Search by title, author, or ISBN
- ✅ Cannot delete issued books (safety check)
- ✅ Prevent issuing unavailable books

### 👥 **User Management**
- ✅ User registration with email validation
- ✅ Admin can delete users
- ✅ Role management (Admin/Student)
- ✅ User search functionality
- ✅ View user creation date

### 📤 **Book Transactions**
- ✅ Issue books to students (14-day due date)
- ✅ Return books with fine calculation
- ✅ Automatic overdue detection
- ✅ Fine: ₹5 per day after due date
- ✅ View transaction history
- ✅ Status tracking (Issued/Returned)

### 📊 **Analytics & Dashboard**
- ✅ Admin dashboard with quick stats
- ✅ Chart.js integration for visualization
- ✅ Books distribution chart
- ✅ Transaction status pie chart
- ✅ Monthly fine collection chart
- ✅ Overdue books tracking
- ✅ Total students count

### 🎨 **Premium UI/UX**
- ✅ Modern responsive design
- ✅ Sidebar navigation
- ✅ Mobile-friendly layout
- ✅ Gradient backgrounds
- ✅ Smooth animations
- ✅ Professional spacing and typography
- ✅ Dark sidebar with light theme main content
- ✅ Cards with hover effects
- ✅ Color-coded status badges

### 🔍 **Search & Filter**
- ✅ Search books by title, author, ISBN
- ✅ Search users by username and email
- ✅ Search within admin panel
- ✅ Quick filters

---

## 👨‍💼 Admin Features

### Dashboard
- View total books, issued, returned, and fine statistics
- Monitor overdue books
- See total students

### Book Management
- Add new books with copies count
- Edit book details
- Delete books (if not issued)
- Search books
- View availability status

### User Management
- View all students
- Search users
- Change user roles (Admin/Student)
- Delete users (excluding admins)

### Transactions
- View all transaction history
- See issuing and return dates
- Monitor fines
- Track book status

---

## 👤 Student Features

### Dashboard
- Browse all available books
- View book details and availability
- Issue books (max 14 days)
- View my transactions
- Return issued books
- Pay fines automatically
- See overdue book warnings

### Book Browsing
- See books in card layout
- View ISBN and author details
- See available copies
- Issue available books

### My Transactions
- View all issued books
- See due dates and return dates
- Pay calculated fines
- View transaction history

---

## 🗄️ Database Schema

### **Users Table**
```sql
- id: INTEGER PRIMARY KEY
- username: TEXT UNIQUE NOT NULL
- password: TEXT NOT NULL (hashed)
- role: TEXT (admin/student)
- email: TEXT
- created_at: TIMESTAMP
```

### **Books Table**
```sql
- id: INTEGER PRIMARY KEY
- title: TEXT NOT NULL
- author: TEXT NOT NULL
- isbn: TEXT
- total_copies: INTEGER
- available_copies: INTEGER
- created_at: TIMESTAMP
```

### **Transactions Table**
```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER (FOREIGN KEY)
- book_id: INTEGER (FOREIGN KEY)
- issue_date: TEXT
- return_date: TEXT
- due_date: TEXT (14 days from issue)
- fine: INTEGER (default 0)
- status: TEXT (issued/returned)
```

---

## 🔧 Routes & Endpoints

### Authentication
- `GET/POST /` → Login page
- `GET/POST /register` → Registration page
- `GET /logout` → Logout user

### Student Routes
- `GET /dashboard` → View books and transactions
- `GET /issue/<book_id>` → Issue a book
- `GET /return/<transaction_id>` → Return a book

### Admin Routes
- `GET /admin` → Admin dashboard
- `POST /add-book` → Add new book
- `GET/POST /edit-book/<book_id>` → Edit book
- `GET /delete-book/<book_id>` → Delete book
- `GET /users` → View all users
- `GET /delete-user/<user_id>` → Delete user
- `GET /change-role/<user_id>/<role>` → Change user role
- `GET /transactions` → View all transactions
- `GET /api/chart-data` → Get chart data (JSON)

---

## 🎨 UI Components & Styling

### Color Scheme
- **Primary**: `#667eea` (Purple)
- **Secondary**: `#764ba2` (Dark Purple)
- **Success**: `#10b981` (Green)
- **Danger**: `#ef4444` (Red)
- **Warning**: `#f59e0b` (Orange)
- **Info**: `#06b6d4` (Cyan)
- **Background**: `#f8fafc` (Light)
- **Sidebar**: `#1e293b` (Dark)

### Responsive Breakpoints
- **Desktop**: Full layout (1024px+)
- **Tablet**: 2-column grid (768px-1023px)
- **Mobile**: Single column (<768px)

---

## 🔒 Security Measures

1. **Password Hashing**: All passwords are hashed using `werkzeug.security`
2. **Session Management**: User sessions are stored securely
3. **Role-Based Access**: Decorators protect admin-only routes
4. **Input Validation**: Form inputs are validated and sanitized
5. **SQL Injection Prevention**: Parameterized queries used throughout
6. **CORS Ready**: Can be extended with CORS support

---

## 💾 How to Reset Database

To reset the database and start fresh:

```bash
# Delete the database file
rm library.db

# Restart the app - it will recreate the database
python app.py
```

---

## 📋 Testing Scenarios

### Test Admin Features
1. Login with admin credentials
2. Add a new book
3. Edit book details
4. Add a student user
5. View admin dashboard
6. Check charts
7. Delete a book (if no transactions)

### Test Student Features
1. Register as a new student
2. Login with student account
3. Issue a book
4. View my transactions
5. Return the book
6. See the fine calculated (if overdue)

### Test Search
1. Search books in admin panel
2. Search users in user management
3. Filter by different criteria

---

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is in use, modify `app.py`:
```python
app.run(debug=True, host='localhost', port=5001)  # Change port
```

### Database Issues
```bash
# Delete corrupted database
del library.db

# Or restart app - it auto-creates
```

### Import Errors
```bash
# Install missing packages
pip install flask werkzeug
```

### CSS Not Loading
- Clear browser cache (Ctrl+Shift+Delete)
- Check if `static/style.css` exists
- Verify correct path in template

---

## 🚀 Production Deployment

### For Production:
1. Set `debug=False`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Use environment variables for secrets
4. Enable HTTPS
5. Use a real database (PostgreSQL)
6. Implement rate limiting
7. Add logging and monitoring

### Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📝 Example Usage Flow

### Admin Setup
1. Login as admin (admin/admin123)
2. Go to Admin Dashboard
3. Add books using "Add New Book" form
4. Monitor analytics in the dashboard

### Student Flow
1. Register as new student
2. Login with credentials
3. Browse available books
4. Issue a book
5. View in "My Transactions"
6. Return book before due date
7. View fine if overdue

---

## 🎓 Educational Features

Perfect for **school projects** because:
- ✅ Complete CRUD operations
- ✅ Database design with relationships
- ✅ User authentication and authorization
- ✅ Modern web technologies (Flask, SQLite, HTML/CSS/JS)
- ✅ Charts and analytics
- ✅ Professional code structure
- ✅ Security best practices
- ✅ Clean, readable code with comments
- ✅ Impressive UI/UX
- ✅ Fully functional features

---

## 📞 Support & Questions

For issues or questions:
1. Check the troubleshooting section
2. Verify all files are in correct folders
3. Ensure Python and Flask are installed
4. Clear browser cache if UI issues occur

---

## 📄 License

This is a school project management system. Feel free to use and modify for educational purposes.

---

## 🎉 Conclusion

Your Library Management System is now **production-ready** with:
- ✨ Premium UI with responsive design
- 🔐 Secure authentication and authorization
- 📊 Analytics and charting
- ✅ All required features implemented
- 🚀 Professional code structure
- 📱 Mobile-friendly interface

**Happy coding! 🚀**
