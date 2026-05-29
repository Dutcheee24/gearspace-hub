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
    # Pag-ayos sa PostgreSQL dialect para kay Render
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback sa local XAMPP MySQL kung wala sa cloud
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/booking_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =========================================================
# 🗂️ DATABASE MODEL (Eksaktong tugma sa index.html)
# =========================================================
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False) # Tugma sa item.item_name
    category = db.Column(db.String(100), nullable=False)  # Tugma sa item.category
    status = db.Column(db.String(50), default='Available') # Tugma sa item.status
    borrower = db.Column(db.String(100), nullable=True)   # Tugma sa item.borrower

    def __repr__(self):
        return f'<Resource {self.item_name}>'

# =========================================================
# 🌐 ROUTES / CONTROLLERS
# =========================================================

# 1. HOMEPAGE (Nagpapakita ng Data at Dashboard Counters)
@app.route('/')
def index():
    try:
        # Kukuha ng lahat ng items mula sa database
        all_items = Resource.query.all()
        
        # Pagkalkula para sa mga Dashboard Cards ng HTML mo
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
        print(f"Error loading homepage: {e}")
        return render_template('index.html', items=[], total_items=0, available_count=0, booked_count=0, maintenance_count=0)

# 2. ADD RESOURCE ROUTE (form action="/create")
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
            print(f"Error adding item: {e}")
            
    return redirect(url_for('index'))

# 3. AJAX UPDATE ROUTE (fetch(`/update/${itemId}`))
@app.route('/update/<int:item_id>', methods=['POST'])
def update(item_id):
    item = Resource.query.get_or_404(item_id)
    
    item.item_name = request.form.get('item_name')
    item.category = request.form.get('category')
    item.status = request.form.get('status')
    item.borrower = request.form.get('borrower')
    
    try:
        db.session.commit()
        return '', 200  # Magpapadala ng 'OK' status sa JavaScript AJAX mo
    except Exception as e:
        db.session.rollback()
        print(f"Error updating item {item_id}: {e}")
        return 'Update failed', 500

# 4. DELETE ROUTE (form action="/delete/{{ item.id }}")
@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    item = Resource.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting item {item_id}: {e}")
        
    return redirect(url_for('index'))

# =========================================================
# 🚀 EXECUTION
# =========================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Awtomatikong gagawa ng table kung wala pa sa Postgres
    app.run(debug=True)