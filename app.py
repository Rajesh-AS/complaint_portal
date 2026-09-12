import os
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort
)
from models import db, User, Complaint


# ---------------------------------------------------------------------------
# App factory & configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaint.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ---------------------------------------------------------------------------
# Admin seeding — runs once on first request
# ---------------------------------------------------------------------------

def create_admin():
    """Create the default admin account if it doesn't already exist."""
    admin = User.query.filter_by(email='admin@example.com').first()
    if admin is None:
        admin = User(
            full_name='Admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print(' * Admin account created: admin@example.com / Admin@123')
    else:
        print(' * Admin account already exists.')


# ---------------------------------------------------------------------------
# Auth decorators
# ---------------------------------------------------------------------------

def login_required(f):
    """Decorator: redirect to login if user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: restrict access to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Context processor — make user info available in all templates
# ---------------------------------------------------------------------------

@app.context_processor
def inject_user():
    """Inject current user into every template context."""
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)


# ---------------------------------------------------------------------------
# PUBLIC ROUTES
# ---------------------------------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not full_name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        # Create user
        user = User(full_name=full_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.full_name}!', 'success')

            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ---------------------------------------------------------------------------
# USER ROUTES
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    complaints = Complaint.query.filter_by(user_id=user.id).order_by(Complaint.created_at.desc()).all()

    stats = {
        'total': len(complaints),
        'pending': sum(1 for c in complaints if c.status == 'Pending'),
        'in_progress': sum(1 for c in complaints if c.status == 'In Progress'),
        'resolved': sum(1 for c in complaints if c.status == 'Resolved'),
        'rejected': sum(1 for c in complaints if c.status == 'Rejected'),
    }

    recent = complaints[:5]  # latest 5
    return render_template('dashboard.html', user=user, stats=stats, recent=recent)


@app.route('/complaint/new', methods=['GET', 'POST'])
@login_required
def new_complaint():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'General')
        priority = request.form.get('priority', 'Medium')

        if not title or not description:
            flash('Title and description are required.', 'danger')
            return render_template('complaint_form.html',
                                   categories=Complaint.CATEGORIES,
                                   priorities=Complaint.PRIORITIES)

        if category not in Complaint.CATEGORIES:
            category = 'General'
        if priority not in Complaint.PRIORITIES:
            priority = 'Medium'

        complaint = Complaint(
            user_id=session['user_id'],
            title=title,
            description=description,
            category=category,
            priority=priority,
            status='Pending'
        )
        db.session.add(complaint)
        db.session.commit()

        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('complaints'))

    return render_template('complaint_form.html',
                           categories=Complaint.CATEGORIES,
                           priorities=Complaint.PRIORITIES)


@app.route('/complaints')
@login_required
def complaints():
    # Filters
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')

    query = Complaint.query.filter_by(user_id=session['user_id'])

    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)

    user_complaints = query.order_by(Complaint.created_at.desc()).all()
    return render_template('complaints.html',
                           complaints=user_complaints,
                           categories=Complaint.CATEGORIES,
                           priorities=Complaint.PRIORITIES,
                           statuses=Complaint.STATUSES,
                           current_status=status_filter,
                           current_category=category_filter,
                           current_priority=priority_filter)


@app.route('/complaint/<int:id>')
@login_required
def complaint_detail(id):
    complaint = Complaint.query.get_or_404(id)

    # Ownership check — normal users can only view their own
    if complaint.user_id != session['user_id'] and not session.get('is_admin'):
        abort(403)

    return render_template('complaint_detail.html', complaint=complaint)


# ---------------------------------------------------------------------------
# ADMIN ROUTES
# ---------------------------------------------------------------------------

@app.route('/admin')
@admin_required
def admin_dashboard():
    complaints = Complaint.query.all()
    stats = {
        'total': len(complaints),
        'pending': sum(1 for c in complaints if c.status == 'Pending'),
        'in_progress': sum(1 for c in complaints if c.status == 'In Progress'),
        'resolved': sum(1 for c in complaints if c.status == 'Resolved'),
        'rejected': sum(1 for c in complaints if c.status == 'Rejected'),
    }
    recent = Complaint.query.order_by(Complaint.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent=recent)


@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')
    search = request.args.get('search', '').strip()

    query = Complaint.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if search:
        query = query.filter(
            (Complaint.title.ilike(f'%{search}%')) |
            (Complaint.description.ilike(f'%{search}%'))
        )

    all_complaints = query.order_by(Complaint.created_at.desc()).all()
    return render_template('admin/complaints.html',
                           complaints=all_complaints,
                           categories=Complaint.CATEGORIES,
                           priorities=Complaint.PRIORITIES,
                           statuses=Complaint.STATUSES,
                           current_status=status_filter,
                           current_category=category_filter,
                           current_priority=priority_filter,
                           current_search=search)


@app.route('/admin/complaint/<int:id>')
@admin_required
def admin_complaint_detail(id):
    complaint = Complaint.query.get_or_404(id)
    return render_template('admin/complaint_detail.html',
                           complaint=complaint,
                           statuses=Complaint.STATUSES)


@app.route('/admin/complaint/<int:id>/update', methods=['POST'])
@admin_required
def admin_update_complaint(id):
    complaint = Complaint.query.get_or_404(id)

    new_status = request.form.get('status', complaint.status)
    admin_response = request.form.get('admin_response', '').strip()

    if new_status in Complaint.STATUSES:
        complaint.status = new_status
    if admin_response:
        complaint.admin_response = admin_response

    complaint.updated_at = datetime.utcnow()
    db.session.commit()

    flash('Complaint updated successfully!', 'success')
    return redirect(url_for('admin_complaint_detail', id=id))


# ---------------------------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------------------------

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
