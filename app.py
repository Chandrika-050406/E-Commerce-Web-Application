from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))

# Product Table
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)

# Order Table
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    status = db.Column(db.String(50))

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session['user'] = username
            session['role'] = user.role
            return redirect('/')

    return render_template('login.html')

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(id)
    session.modified = True
    return redirect('/')

@app.route('/cart')
def cart():
    ids = session.get('cart', [])
    products = Product.query.filter(Product.id.in_(ids)).all()
    return render_template('cart.html', products=products)

@app.route('/checkout')
def checkout():

    ids = session.get('cart', [])

    products = Product.query.filter(Product.id.in_(ids)).all()

    for product in products:
        order = Order(
            username=session['user'],
            product_name=product.name,
            status="Processing"
        )
        db.session.add(order)

    db.session.commit()
    session['cart'] = []

    return redirect('/orders')

@app.route('/orders')
def orders():
    orders = Order.query.filter_by(
        username=session['user']
    ).all()

    return render_template('orders.html', orders=orders)

@app.route('/admin')
def admin():

    if session.get('role') != 'admin':
        return "Access Denied"

    products = Product.query.all()

    return render_template(
        'admin.html',
        products=products
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if Product.query.count() == 0:
            db.session.add(Product(name="Laptop", price=50000))
            db.session.add(Product(name="Phone", price=20000))
            db.session.add(Product(name="Headphones", price=3000))
            db.session.commit()

    app.run(debug=True)