from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from passlib.hash import sha256_crypt
import pymysql

# Use PyMySQL instead of MySQLdb
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'account'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/user_signup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Recommended to silence warnings
app.permanent_session_lifetime = timedelta(days=10)  # Session 10 din tak valid rahe
db = SQLAlchemy(app)

class Contact(db.Model):  
    countid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    emailid = db.Column(db.String(100), nullable=False)
    mobilenumber = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=False)
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        address = request.form.get('address')
        message = request.form.get('message')

        # Check if email OR mobile already exists
        existing_contact = Contact.query.filter(
            (Contact.emailid == email) | (Contact.mobilenumber == mobile)
        ).first()

        if existing_contact:
            # ❌ User already exists
            return render_template('contact.html', error=True)

        # ✅ New user - save to DB
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
# GET request
    return render_template('contact.html')
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
@app.route('/')
def index():
    return render_template('index.html') 
@app.route('/order')
def order():
    return render_template('order.html') 
@app.route('/addtocart')
def addtocartbn():
    return render_template('addtocart.html') 

@app.route('/electronics')
def electronics():
    return render_template('electronics.html')

@app.route('/Stationery')
def Stationeryitems():
    return render_template('Stationery.html')

@app.route('/Gaming')
def Gamingitems():
    return render_template('Gaming.html') 

class Registrations(db.Model):
    usernameid  = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    emailid = db.Column(db.String(100), unique=True, nullable=False)
    mobilenumber = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/account', methods=['GET', 'POST'])
def accountpage():
    if request.method == 'POST':
        name=request.form['name'],
        email=request.form['email'],
        mobile=request.form['mobile'],
        password=request.form['password']
        encpasswored=sha256_crypt.encrypt(password)
        
        # Create a new Contact object
        entry = Registrations(
        username=name,
        emailid=email,
        mobilenumber=mobile,
        password=encpasswored
)
 # Save to DB
         try:
            db.session.add(entry)
            db.session.commit()
            flash("Registration Complete ✅", "success")
            return redirect(url_for('login'))  # Redirect to login page
        except Exception as e:
            db.session.rollback()
            flash("Registration failed ❌. Try again.", "error")
            print(e)  # Log the error for debugging
            return render_template('account.html')  # Show form again with message

    return render_template('account.html')
@app.route('/kidsproduct')
def kidsproduct():
    return render_template('kidsproduct.html')
    
@app.route('/clothingproduct')
def clothingproduct():
    return render_template('clothingproduct.html')
@app.route('/toys')
def toys():
    return render_template('toys.html')  
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Agar already login hai to direct dashboard pe bhejo
    if 'username' in session:
        return redirect(url_for('result'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Registrations.query.filter_by(username=username).first()

        if user and sha256_crypt.verify(password, user.password):
            session.permanent = True  # Permanent session bana dein
            session['username'] = user.username  
            flash("Login successful ✅", "success")
            return redirect(url_for('result'))  
        else:
            flash("Invalid username or password ❌", "error")
            return render_template('login.html')  
    return render_template('login.html')
# Dashboard / Result route
@app.route('/result')
def result():
    if 'username' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))
    
    user = Registrations.query.filter_by(username=session['username']).first()
    return render_template('result.html',
                        username=user.username,
                        emailid=user.emailid,
                        password=user.password)   # Assuming user.email hai
# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))
@app.route('/checkout')
def checkout():
    if 'username' not in session:
        flash("Please login first to place order.", "warning")
        return redirect(url_for('login'))
    return render_template('checkout.html')
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
