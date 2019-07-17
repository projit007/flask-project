from flask import *
from flask_sqlalchemy import *
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345@localhost/api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'projit'

db = SQLAlchemy(app)


class Employee(db.Model):
    __tablename__= 'employee'
    fname = db.Column('fname', db.String(255))
    lname = db.Column('lname', db.String(255))
    phone = db.Column('phone', db.String(255))
    email = db.Column('email', db.String(255), primary_key=True)
    password = db.Column('password', db.String(255))
    dob = db.Column('dob', db.String(255))
    state = db.Column('state', db.String(255))
    city = db.Column('city', db.String(255))
    image = db.Column('image', db.String(255))


mail = Employee.query.filter_by(email='test@gmail.com').first()
print(mail.fname)


@app.route('/', methods=['POST', 'GET'])
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['email'])
    return render_template('home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ''
    if 'loggedin' in session:
        return render_template('home.html', username=session['email'])
    if request.method == "POST":
        details = request.form
        l_password = details['password']
        l_email = details['username']
        hashed_password = Employee.query.filter_by(email=l_email).first()
        hashed_password = hashed_password.password
        hashed_password = ''.join(hashed_password)
        verify_password = check_password_hash(hashed_password, l_password)
        if verify_password:
            record = Employee.query.filter_by(email=l_email).first()
            print(record.email)
            session['loggedin'] = True
            session['email'] = record.email
            return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', msg=error)


@app.route('/register', methods=['POST', 'GET'])
def register():
    msg = ''
    if request.method == 'POST' and 'lname' in request.form and 'fname' in request.form and 'password' in request.form and 'email' in request.form:
        f_name = request.form['fname']
        l_name = request.form['lname']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method="sha256")
        print(hashed_password)
        email = request.form['email']
        #print(email)
        account = Employee.query.filter_by(email=email).all()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z]+', f_name):
            msg = 'No special character or number!'
        elif not re.match(r'[A-Za-z]+', l_name):
            msg = 'No special character or number!'
        elif not l_name or not f_name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            reg = Employee(fname=f_name, lname=l_name, email=email, password=hashed_password)
            db.session.add(reg)
            db.session.commit()
            msg = 'You have successfully registered!'
            return render_template('login.html')
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return render_template('home.html')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if 'loggedin' in session:
        msg = ''
        print(session['email'])
        if request.args:
            msg = request.args['msg']
        account = Employee.query.filter_by(email=session['email']).first()
        return render_template('profile.html', fname=account.fname, lname=account.lname, phone=account.phone, email=account.email, dob=account.dob, state=account.state, city=account.city, user_image=account.image, msg=msg)
    return redirect(url_for('login'))


@app.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    account = Employee.query.filter_by(email=session['email']).first()
    if request.method == "POST":
        phone = request.form['phone']
        dob = request.form['dob']
        state = request.form['state']
        city = request.form['city']

        # Image upload================
        image = request.files["pic"]
        if image.filename:
            image.save(os.path.join(os.getcwd() + '/static/upload_images', image.filename))

        # update database==================
        update = Employee.query.filter_by(email=session['email']).first()
        update.phone = phone
        update.dob = dob
        update.state = state
        update.city = city
        update.image = image.filename
        db.session.commit()
        msg = 'Profile successfully updated'
        return redirect(url_for('profile', msg=msg))
    return render_template('edit_profile.html', fname=account.fname, lname=account.lname, phone=account.phone, email=account.email, dob=account.dob, state=account.state, city=account.city, user_image=account.image)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)