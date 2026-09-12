# Online Complaint Management System

A full-stack web application built with Python Flask for submitting, tracking, and managing complaints.

## Features

- User registration & login with secure password hashing
- Submit complaints with categories and priorities
- Track complaint status (Pending → In Progress → Resolved / Rejected)
- Admin dashboard to manage all complaints
- Admin can update status and add responses
- Search and filter complaints
- Responsive, professional UI
- Role-based access control

## Tech Stack

- **Backend:** Python 3.12, Flask
- **Database:** SQLite with Flask-SQLAlchemy
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Auth:** Flask sessions, Werkzeug password hashing

## Setup

```bash
# 1. Navigate to the project directory
cd complaint_portal

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

Open: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Credentials

### Admin Account
- **Email:** admin@example.com
- **Password:** Admin@123

### Test User
- Register a new account through the registration page.

## Project Structure

```
complaint_portal/
├── venv/
├── instance/
│   └── complaint.db
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── complaint_form.html
│   ├── complaints.html
│   ├── complaint_detail.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── complaints.html
│   │   └── complaint_detail.html
│   └── errors/
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── app.py
├── models.py
├── requirements.txt
└── README.md
```

## License

This project is for educational purposes.
