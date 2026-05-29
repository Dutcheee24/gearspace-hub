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
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/booking_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =========================================================
# 🗂️ DATABASE MODEL (Para sa GearSpace Hub)
# =========================================================
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Available')
    borrower = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Resource {self.resource_name}>'

# =========================================================
# 🌐 ROUTES / PAGES
# =========================================================
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return save_resource_logic()
    
    try:
        resources = Resource.query.all()
        return render_template('index.html', resources=resources, items=resources, data=resources, bookings=resources)
    except Exception as e:
        return render_template('index.html')

# Sinasalo nito ang kahit anong isinulat ninyong "action" URL sa HTML form
@app.route('/create', methods=['GET', 'POST'])
def create(): return save_resource_logic()

@app.route('/add', methods=['POST'])
def add(): return save_resource_logic()

@app.route('/add_resource', methods=['POST'])
def add_resource(): return save_resource_logic()

@app.route('/add_item', methods=['POST'])
def add_item(): return save_resource_logic()

def save_resource_logic():
    name = request.form.get('resource_name') or request.form.get('name') or request.form.get('resourceName') or request.form.get('item_name')
    cat = request.form.get('category') or request.form.get('resource_category') or request.form.get('item_category')
    stat = request.form.get('status') or request.form.get('resource_status') or 'Available'
    rem = request.form.get('borrower_name') or request.form.get('borrower') or request.form.get('remarks') or request.form.get('borrower_remarks')

    if name and cat:
        try:
            new_resource = Resource(resource_name=name, category=cat, status=stat, borrower=rem)
            db.session.add(new_resource)
            db.session.commit()
            flash('Successfully added to GearSpace Hub!')
        except Exception as e:
            db.session.rollback()
            print(f"Database Error: {e}")
            
    return redirect(url_for('index'))

# =========================================================
# 🚀 PAGPAPATAKBO NG APP
# =========================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)