from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from passlib.hash import sha256_crypt
import pymysql
import os

pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.secret_key = os.environ.get(
    'SECRET_KEY',
    'dev-secret-key'
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.permanent_session_lifetime = timedelta(days=10)

db = SQLAlchemy(app)




# ---------------- DATABASE MODELS ----------------

class Contact(db.Model):
    countid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    emailid = db.Column(db.String(100), nullable=False)
    mobilenumber = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=False)


class Registrations(db.Model):
    usernameid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    emailid = db.Column(db.String(100), unique=True, nullable=False)
    mobilenumber = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    
    
    # ---------------- PURCHASE MODEL ----------------

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Kis user ne purchase ki
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('registrations.usernameid'),
        nullable=False
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    product_name = db.Column(
        db.String(200),
        nullable=False
    )

    image = db.Column(
        db.String(500),
        nullable=True
    )

    price = db.Column(
        db.Float,
        default=0
    )

    original_price = db.Column(
        db.Float,
        default=0
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    total = db.Column(
        db.Float,
        default=0
    )

    payment_method = db.Column(
        db.String(100),
        default='COD'
    )

    status = db.Column(
        db.String(50),
        default='Placed'
    )

    order_id = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        address = request.form.get('address')
        message = request.form.get('message')

        existing_contact = Contact.query.filter(
            (Contact.emailid == email) | (Contact.mobilenumber == mobile)
        ).first()

        if existing_contact:
            return render_template('contact.html', error=True)

        entry = Contact(
            name=name,
            emailid=email,
            mobilenumber=mobile,
            address=address,
            message=message
        )

        db.session.add(entry)
        db.session.commit()

        return render_template('contact.html', success=True)

    return render_template('contact.html')


# ---------------- SEARCH ----------------

category = {
    'man': 'clothingproduct.html',
    'woman': 'clothingproduct.html',
    'kids': 'kidsproduct.html',
    'electronic': 'electronics.html',
    'gaming': 'gaming.html',
    'stationery': 'stationery.html',
    'toys': 'toys.html',
}

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('search', '').strip().lower()

    if query in category:
        return render_template(category[query])
    else:
        return "Category not found", 404


# ---------------- STATIC PAGES ----------------



from flask import jsonify, session

@app.route('/api/login-status')
def login_status():
    return jsonify({
        "logged_in": bool(session.get("user_id"))
    })

@app.route('/order')
def order():

    if 'user_id' not in session:
        flash(
            "Please login first to place order.",
            "warning"
        )
        return redirect(url_for('login'))

    user = Registrations.query.filter_by(
        usernameid=session['user_id']
    ).first()

    if not user:
        session.clear()

        flash(
            "User account not found. Please login again.",
            "error"
        )

        return redirect(url_for('login'))

    return render_template(
        'order.html',
        user=user
    )


@app.route('/addtocart')
def addtocart():

    user_logged_in = 'username' in session

    return render_template(
        'addtocart.html',
        user_logged_in=user_logged_in
    )
    # ---------------- SAVE PURCHASE ----------------
# =========================================================
# SAVE ORDER FROM ORDER PAGE
# =========================================================

@app.route('/save-purchase', methods=['POST'])
def save_purchase():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------
    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    # -----------------------------------------------------
    # CURRENT LOGGED-IN USER
    # -----------------------------------------------------
    user = Registrations.query.filter_by(
        usernameid=session['user_id']
    ).first()

    if not user:
        session.clear()

        return jsonify({
            "success": False,
            "message": "User account not found."
        }), 401

    # -----------------------------------------------------
    # GET JSON DATA FROM order.html
    # -----------------------------------------------------
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid order data."
        }), 400

    # -----------------------------------------------------
    # CART ITEMS
    # -----------------------------------------------------
    items = data.get('items', [])

    if not items or not isinstance(items, list):
        return jsonify({
            "success": False,
            "message": "Your cart is empty."
        }), 400

    # -----------------------------------------------------
    # CUSTOMER / DELIVERY DATA
    # -----------------------------------------------------
    address = str(data.get('address', '')).strip()
    city = str(data.get('city', '')).strip()
    state = str(data.get('state', '')).strip()
    pincode = str(data.get('pincode', '')).strip()
    country = str(data.get('country', 'India')).strip()
    address_type = str(data.get('addressType', 'Home')).strip()

    # -----------------------------------------------------
    # PAYMENT + DELIVERY
    # -----------------------------------------------------
    payment = str(
        data.get('payment', 'cod')
    ).strip().lower()

    delivery = str(
        data.get('delivery', 'fast')
    ).strip().lower()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------
    if not address:
        return jsonify({
            "success": False,
            "message": "Please enter your complete address."
        }), 400

    if not city:
        return jsonify({
            "success": False,
            "message": "Please enter your city."
        }), 400

    if not state:
        return jsonify({
            "success": False,
            "message": "Please enter your state."
        }), 400

    if not pincode.isdigit() or len(pincode) != 6:
        return jsonify({
            "success": False,
            "message": "Please enter a valid 6-digit PIN code."
        }), 400

    # -----------------------------------------------------
    # PAYMENT DISPLAY NAME
    # -----------------------------------------------------
    payment_names = {
        'cod': 'COD',
        'upi': 'UPI',
        'card': 'CARD'
    }

    payment_method = payment_names.get(
        payment,
        'COD'
    )

    # -----------------------------------------------------
    # GENERATE ONE ORDER ID
    # -----------------------------------------------------
    from datetime import datetime
    import uuid

    order_id = (
        "ORD-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )

    # -----------------------------------------------------
    # SAVE EVERY CART PRODUCT
    # -----------------------------------------------------
    saved_items = []

    try:

        for item in items:

            product_name = str(
                item.get('name', 'Product')
            ).strip()

            image = str(
                item.get('image', '')
            ).strip()

            try:
                price = float(
                    item.get('price', 0) or 0
                )
            except (TypeError, ValueError):
                price = 0

            try:
                original_price = float(
                    item.get(
                        'originalPrice',
                        price
                    ) or price
                )
            except (TypeError, ValueError):
                original_price = price

            try:
                quantity = int(
                    item.get('quantity', 1) or 1
                )
            except (TypeError, ValueError):
                quantity = 1

            # Safety
            if quantity < 1:
                quantity = 1

            if price < 0:
                price = 0

            if original_price < 0:
                original_price = price

            # Product total
            total = price * quantity

            # -------------------------------------------------
            # CREATE PURCHASE
            # -------------------------------------------------
            purchase = Purchase(

                user_id=user.usernameid,

                username=user.username,

                product_name=product_name,

                image=image,

                price=price,

                original_price=original_price,

                quantity=quantity,

                total=total,

                payment_method=payment_method,

                status='Placed',

                order_id=order_id
            )

            db.session.add(purchase)

            saved_items.append({
                "name": product_name,
                "quantity": quantity,
                "total": total
            })

        # -----------------------------------------------------
        # COMMIT ALL PRODUCTS TO DATABASE
        # -----------------------------------------------------
        db.session.commit()

        # -----------------------------------------------------
        # SAVE DELIVERY INFO IN SESSION
        # OPTIONAL
        # -----------------------------------------------------
        session['last_order_id'] = order_id

        session['last_order_address'] = {
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "country": country,
            "address_type": address_type,
            "delivery": delivery
        }

        # -----------------------------------------------------
        # SUCCESS RESPONSE
        # -----------------------------------------------------
        return jsonify({
            "success": True,
            "message": "Order placed successfully.",
            "order_id": order_id,
            "items": saved_items
        })

    except Exception as e:

        db.session.rollback()

        print(
            "SAVE PURCHASE ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Order save failed."
        }), 500


@app.route('/electronics')
def electronics():
    return render_template('electronics.html')


@app.route('/Stationery')
def stationery():
    return render_template('stationery.html')


@app.route('/Gaming')
def gaming():
    return render_template('gaming.html')


@app.route('/kidsproduct')
def kidsproduct():
    return render_template('kidsproduct.html')


@app.route('/clothingproduct')
def clothingproduct():
    return render_template('clothingproduct.html')


@app.route('/toys')
def toys():
    return render_template('toys.html')

# ---------------- ACCOUNT REGISTER ----------------

@app.route('/account', methods=['GET', 'POST'])
def accountpage():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not mobile or not password:
            flash("Please fill all fields ❌", "error")
            return render_template('account.html')

        enc_password = sha256_crypt.hash(password)

        entry = Registrations(
            username=name,
            emailid=email,
            mobilenumber=mobile,
            password=enc_password
        )

        try:

            db.session.add(entry)
            db.session.commit()

            flash(
                "Registration Complete ✅ Please login to continue.",
                "success"
            )

            # Registration ke baad DIRECT LOGIN PAGE
            return redirect(url_for('login'))

        except Exception as e:

            db.session.rollback()

            print("Registration Error:", e)

            flash(
                "Registration failed ❌",
                "error"
            )

            return render_template(
                'account.html'
            )

    return render_template('account.html')


# ---------------- LOGIN ----------------
# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    # Already logged in
    if 'user_id' in session:
        return redirect(url_for('result'))

    if request.method == 'POST':

        username = request.form.get(
            'username',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        if not username or not password:

            flash(
                "Please enter username and password ❌",
                "error"
            )

            return render_template('login.html')

        user = Registrations.query.filter_by(
            username=username
        ).first()

        if user and sha256_crypt.verify(
            password,
            user.password
        ):

            # Permanent session
            session.permanent = True

            # IMPORTANT
            session['user_id'] = user.usernameid
            session['username'] = user.username
            session['emailid'] = user.emailid

            flash(
                "Login successful ✅",
                "success"
            )

            return redirect(
                url_for('result')
            )

        flash(
            "Invalid username or password ❌",
            "error"
        )

        return render_template('login.html')

    return render_template('login.html')

# ---------------- USER DASHBOARD ----------------
# ---------------- USER DASHBOARD ----------------
# ---------------- USER DASHBOARD ----------------

@app.route('/result')
def result():

    # Login required
    if 'user_id' not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for('login')
        )

    # Logged-in user ID
    user_id = session['user_id']

    # Find current user
    user = Registrations.query.filter_by(
        usernameid=user_id
    ).first()

    if not user:

        session.clear()

        flash(
            "User account not found. Please login again.",
            "error"
        )

        return redirect(
            url_for('login')
        )

    # -------------------------------------------------
    # CURRENT USER PURCHASES ONLY
    # -------------------------------------------------

    orders = Purchase.query.filter_by(
        user_id=user.usernameid
    ).order_by(
        Purchase.created_at.desc()
    ).all()

    # -------------------------------------------------
    # STATISTICS
    # -------------------------------------------------

    total_orders = len(orders)

    total_spent = sum(
        float(order.total or 0)
        for order in orders
    )

    total_products = sum(
        int(order.quantity or 1)
        for order in orders
    )

    # -------------------------------------------------
    # CURRENT MONTH
    # -------------------------------------------------

    from datetime import datetime

    now = datetime.now()

    monthly_spent = sum(
        float(order.total or 0)
        for order in orders
        if order.created_at
        and order.created_at.month == now.month
        and order.created_at.year == now.year
    )

    # -------------------------------------------------
    # ORDER STATUS
    # -------------------------------------------------

    confirmed_orders = sum(
        1
        for order in orders
        if str(order.status or '').lower()
        in [
            'placed',
            'confirmed',
            'delivered',
            'success'
        ]
    )

    pending_orders = sum(
        1
        for order in orders
        if 'pending' in str(order.status or '').lower()
    )

    cancelled_orders = sum(
        1
        for order in orders
        if 'cancel' in str(order.status or '').lower()
    )

    # -------------------------------------------------
    # MONTHLY CHART
    # -------------------------------------------------

    monthly_data = [0] * 12

    for order in orders:

        if order.created_at:

            month_index = order.created_at.month - 1

            monthly_data[month_index] += float(
                order.total or 0
            )

    # -------------------------------------------------
    # CART COUNT
    # -------------------------------------------------

    # Abhi cart database model nahi hai,
    # isliye 0 rakha hai.
    cart_count = 0

    # -------------------------------------------------
    # DASHBOARD
    # -------------------------------------------------

    return render_template(
        'result.html',

        username=user.username,

        emailid=user.emailid,

        orders=orders,

        total_orders=total_orders,

        total_spent=total_spent,

        total_products=total_products,

        monthly_spent=monthly_spent,

        monthly_data=monthly_data,

        confirmed_orders=confirmed_orders,

        pending_orders=pending_orders,

        cancelled_orders=cancelled_orders,

        cart_count=cart_count
    )
# ---------------- LOGOUT ----------------
@app.route('/logout', methods=['POST'])
def logout():

    # User session completely clear
    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    # Logout ke baad direct home/index page
    return redirect(
        url_for('home')
    )

# ---------------- MAIN ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run()
