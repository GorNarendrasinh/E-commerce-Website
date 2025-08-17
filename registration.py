# from flask import Flask, render_template, request, redirect , url_for , flash
# from flask_sqlalchemy import SQLAlchemy
# from passlib.hash import sha256_crypt

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/user_signup'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# class Registrations(db.Model):
#     usernameid  = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), nullable=False)
#     emailid = db.Column(db.String(100), unique=True, nullable=False)
#     mobilenumber = db.Column(db.String(15), nullable=False)
#     password = db.Column(db.String(100), nullable=False)

# @app.route('/account', methods=['GET', 'POST'])
# def accountpage():
#     if request.method == 'POST':
#     username=request.form['username'],
#     email=request.form['email'],
#     mobile=request.form['mobile'],
#     password=request.form['password']
#     encpasswored=sha256_crypt.encrypt(password)
        
#         # Create a new Contact object
#         entry = Contact(
#             username=name,
#             emailid=email,
#             mobilenumber=mobile,
#             password=encpasswored,
           
#         )

#         # Save to DB
#         try:
#             db.session.add(entry)
#             db.session.commit()
#              flash("Registrations Complate..")
#             return render_template(url_for('account'))
#         except:
#             flash("tryy again user")
#             return render_template(url_for('account'))

#         return render_template('account.html', success=True)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # creates the table if it doesn't exist
#     app.run(debug=True)
