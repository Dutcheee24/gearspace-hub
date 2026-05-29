from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Konektado sa iyong local MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Binagong Model para sa Facilities at Equipment
class BookingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)  # Hal. Gymnasium, Projector
    category = db.Column(db.String(100), nullable=False)   # Hal. Facility, Equipment
    status = db.Column(db.String(50), nullable=False, default="Available") # Available, Booked, Maintenance
    borrower = db.Column(db.String(100), nullable=True, default="") # Pangalan ng nag-book o hiram

with app.app_context():
     db.create_all()

@app.route('/')
def index():
    items = BookingItem.query.all()
    total_items = len(items)
    available_count = len([i for i in items if i.status == "Available"])
    booked_count = len([i for i in items if i.status == "Booked"])
    maintenance_count = len([i for i in items if i.status == "Maintenance"])

    return render_template(
        'index.html',
        items=items,
        total_items=total_items,
        available_count=available_count,
        booked_count=booked_count,
        maintenance_count=maintenance_count
    )

@app.route('/create', methods=['POST'])
def create_item():
    item_name = request.form['item_name']
    category = request.form['category']
    status = request.form['status']
    borrower = request.form.get('borrower', '')

    new_item = BookingItem(
        item_name=item_name,
        category=category,
        status=status,
        borrower=borrower
    )

    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    item = BookingItem.query.get(item_id)

    if item:
        item.item_name = request.form['item_name']
        item.category = request.form['category']
        item.status = request.form['status']
        item.borrower = request.form.get('borrower', '')

        db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = BookingItem.query.get(item_id)
    if item:
       db.session.delete(item)
       db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)