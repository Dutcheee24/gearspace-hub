import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'gearspace_secret_key'

# =========================================================
# 🛠️ DATABASE CONFIGURATION
# =========================================================
database_url = os.environ.get('DATABASE_URL')

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/booking_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =========================================================
# 🗂️ DATABASE MODEL (May Bagong Table Name para sa Cloud)
# =========================================================
class Resource(db.Model):
    __tablename__ = 'gearspace_hub_resources'  # <--- BINAGO: Para mapilitan si Render na gumawa ng sariwang table
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Available')
    borrower = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Resource {self.item_name}>'

# 🔥 IMPORTANTENG DAGDAG: Inilabas sa __main__ para pilit na patakbuhin ni Render/Gunicorn sa startup
with app.app_context():
    db.create_all()

# =========================================================
# 🌐 ROUTES / CONTROLLERS
# =========================================================

@app.route('/')
def index():
    try:
        all_items = Resource.query.all()
        
        # Kalkulasyon para sa mga kulay-kulay na Cards sa itaas ng dashboard mo
        total_items = len(all_items)
        available_count = Resource.query.filter_by(status='Available').count()
        booked_count = Resource.query.filter_by(status='Booked').count()
        maintenance_count = Resource.query.filter_by(status='Maintenance').count()
        
        return render_template('index.html', 
                               items=all_items, 
                               total_items=total_items, 
                               available_count=available_count, 
                               booked_count=booked_count, 
                               maintenance_count=maintenance_count)
    except Exception as e:
        print(f"Database Read Error: {e}")
        return render_template('index.html', items=[], total_items=0, available_count=0, booked_count=0, maintenance_count=0)

@app.route('/create', methods=['POST'])
def create():
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    status = request.form.get('status') or 'Available'
    borrower = request.form.get('borrower')

    if item_name and category:
        try:
            new_item = Resource(item_name=item_name, category=category, status=status, borrower=borrower)
            db.session.add(new_item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Database Write Error: {e}")
            
    return redirect(url_for('index'))

@app.route('/update/<int:item_id>', methods=['POST'])
def update(item_id):
    item = Resource.query.get_or_404(item_id)
    item.item_name = request.form.get('item_name')
    item.category = request.form.get('category')
    item.status = request.form.get('status')
    item.borrower = request.form.get('borrower')
    
    try:
        db.session.commit()
        return '', 200
    except Exception as e:
        db.session.rollback()
        return 'Update failed', 500

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    item = Resource.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Delete Error: {e}")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
