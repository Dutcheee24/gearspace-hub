from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gearspace_super_secret_key'

# ---------------------------------------------------------------------------
# DATABASE CONFIGURATION (MySQL for Local PC, PostgreSQL for Render Cloud)
# ---------------------------------------------------------------------------
database_url = os.environ.get('DATABASE_URL')

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/booking_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'gearspace_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='User') # 'Admin' or 'User'

class Resource(db.Model):
    __tablename__ = 'gearspace_hub_resources'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Available')
    borrower = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(50), nullable=True)  # FEATURE 2: Booking Start
    end_date = db.Column(db.String(50), nullable=True)    # FEATURE 2: Booking End

class ActivityLog(db.Model):
    __tablename__ = 'gearspace_activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)  # FEATURE 3: Audit Trail

# ---------------------------------------------------------------------------
# ROUTES & CORE LOGIC
# ---------------------------------------------------------------------------
@app.route('/')
def dashboard():
    if 'username' not in session:
        return render_template('index.html') # Manghihingi ng login form

    items = Resource.query.all()
    logs = ActivityLog.query.order_by(ActivityLog.id.desc()).limit(8).all()

    # Calculate system analytics
    total_items = len(items)
    available_count = sum(1 for i in items if i.status == 'Available')
    booked_count = sum(1 for i in items if i.status == 'Booked')
    maintenance_count = sum(1 for i in items if i.status == 'Maintenance')

    return render_template(
        'index.html', 
        items=items, 
        logs=logs,
        total_items=total_items, 
        available_count=available_count, 
        booked_count=booked_count, 
        maintenance_count=maintenance_count
    )

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    
    if user:
        session['username'] = user.username
        session['role'] = user.role
        flash('Maligayang pagbabalik!', 'success')
    else:
        flash('Maling username o password!', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))

@app.route('/create', methods=['POST'])
def create():
    if session.get('role') != 'Admin':
        flash('Access Denied: Mga Admin lang ang pwedeng magdagdag!', 'danger')
        return redirect(url_for('dashboard'))

    item_name = request.form.get('item_name')
    category = request.form.get('category')
    status = request.form.get('status')
    borrower = request.form.get('borrower')
    start_date = request.form.get('start_date') or 'N/A'
    end_date = request.form.get('end_date') or 'N/A'

    new_item = Resource(
        item_name=item_name, category=category, status=status, 
        borrower=borrower, start_date=start_date, end_date=end_date
    )
    db.session.add(new_item)
    
    # Log Action
    log = ActivityLog(action=f"➕ idinagdag ni {session['username']} ang '{item_name}'", timestamp=datetime.now().strftime("%I:%M %p"))
    db.session.add(log)
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if session.get('role') != 'Admin':
        flash('Access Denied: Mga Admin lang ang pwedeng mag-edit!', 'danger')
        return redirect(url_for('dashboard'))

    item = Resource.query.get_or_404(id)
    item.item_name = request.form.get('item_name')
    item.category = request.form.get('category')
    item.status = request.form.get('status')
    item.borrower = request.form.get('borrower')
    item.start_date = request.form.get('start_date') or 'N/A'
    item.end_date = request.form.get('end_date') or 'N/A'

    # Log Action
    log = ActivityLog(action=f"📝 In-update ni {session['username']} ang '{item.item_name}' ({item.status})", timestamp=datetime.now().strftime("%I:%M %p"))
    db.session.add(log)

    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if session.get('role') != 'Admin':
        flash('Access Denied: Mga Admin lang ang pwedeng magbura!', 'danger')
        return redirect(url_for('dashboard'))

    item = Resource.query.get_or_404(id)
    
    # Log Action
    log = ActivityLog(action=f"🗑️ Binura ni {session['username']} ang resource na '{item.item_name}'", timestamp=datetime.now().strftime("%I:%M %p"))
    db.session.add(log)

    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ---------------------------------------------------------------------------
# AUTO-DB CREATION & DEFAULT USER SEEDING
# ---------------------------------------------------------------------------
with app.app_context():
    db.create_all()
    # Gumawa ng automatic accounts kung walang laman ang User Table
    if not User.query.first():
        admin = User(username='admin', password='admin123', role='Admin')
        student = User(username='student', password='student123', role='User')
        db.session.add_all([admin, student])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
