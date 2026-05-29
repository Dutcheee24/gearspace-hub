import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'gearspace_secret_key'

# =========================================================
# 🛠️ DATABASE CONFIGURATION (SMART ROUTING)
# =========================================================
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Kung nasa Render (PostgreSQL), inaayos ang prefix para sa SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Kung nasa laptop (XAMPP), gagamitin ang lokal na MySQL mo bilang backup
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/booking_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =========================================================
# 🗂️ DATABASE MODEL (Para sa inyong Booking System)
# =========================================================
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Pending')

    def __repr__(self):
        return f'<Booking {self.id}>'

# =========================================================
# 🌐 ROUTES / PAGES
# =========================================================
@app.route('/')
def index():
    # Ilo-load nito ang index.html mula sa templates folder mo
    try:
        bookings = Booking.query.all()
        return render_template('index.html', bookings=bookings)
    except Exception as e:
        # Kung may error sa pagbasa ng db sa simula, ire-render pa rin ang page
        return render_template('index.html')

# Isang simpleng halimbawang link kung sakaling magse-send kayo ng data mula sa HTML niyo
@app.route('/add_booking', methods=['POST'])
def add_booking():
    if request.method == 'POST':
        name = request.form.get('customer_name')
        item = request.form.get('item_name')
        
        if name and item:
            new_booking = Booking(customer_name=name, item_name=item)
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking successfully added!')
        return redirect(url_for('index'))

# =========================================================
# 🚀 PAGPAPATAKBO NG APP (AUTO-CREATE TABLES)
# =========================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Kusang gagawa ng tables sa database para hindi mag-error!
        
    app.run(debug=True)