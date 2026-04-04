from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'account'

app.permanent_session_lifetime = timedelta(days=10)

# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html')


# ---------------- CONTACT (NO DB) ----------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash("Message sent successfully ✅ (No DB version)", "success")
        return render_template('contact.html')

    return render_template('contact.html')


# ---------------- STATIC PAGES ----------------
@app.route('/order')
def order():
    return render_template('order.html')


@app.route('/addtocart')
def addtocart():
    return render_template('addtocart.html')


@app.route('/electronics')
def electronics():
    return render_template('electronics.html')


@app.route('/Stationery')
def stationery():
    return render_template('Stationery.html')


@app.route('/Gaming')
def gaming():
    return render_template('Gaming.html')


@app.route('/kidsproduct')
def kidsproduct():
    return render_template('kidsproduct.html')


@app.route('/clothingproduct')
def clothingproduct():
    return render_template('clothingproduct.html')


@app.route('/toys')
def toys():
    return render_template('toys.html')


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
    return "Category not found", 404


# ---------------- ACCOUNT (NO DB LOGIN SYSTEM) ----------------
@app.route('/account')
def accountpage():
    return render_template('account.html')


# ---------------- LOGIN (SESSION ONLY DEMO) ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            session['username'] = username
            flash("Login successful ✅", "success")
            return redirect(url_for('result'))

        flash("Invalid input ❌", "error")

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/result')
def result():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('result.html', username=session['username'])


# ---------------- LOGOUT ----------------
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash("Logged out", "info")
    return redirect(url_for('login'))


# ---------------- CHECKOUT ----------------
@app.route('/checkout')
def checkout():
    if 'username' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('login'))

    return render_template('checkout.html')


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
