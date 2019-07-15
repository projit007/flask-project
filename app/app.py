from flask import *
from flask_mysqldb import MySQL as sql
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key= 'projit'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'api'
app.config['UPLOAD_FOLDER'] = 'D:/Projit/Python/MyRestAPI/app/static/upload_images'


mysql = sql(app)


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
        cur = mysql.connection.cursor()
        details = request.form
        l_password = details['password']
        l_email = details['username']
        cur.execute("SELECT password FROM employee WHERE email = %s", [l_email])
        hashed_password = cur.fetchone()
        hashed_password = ''.join(hashed_password)
        verify_password = check_password_hash(hashed_password, l_password)
        if verify_password:
            cur.execute("SELECT email FROM employee WHERE email = %s", [l_email])
            record = cur.fetchone()
            mysql.connection.commit()
            cur.close()

            session['loggedin'] = True
            session['email'] = record[0]
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
        email = request.form['email']
        #print(email)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employee WHERE email = %s", [email])
        account = cur.fetchone()

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
            cur.execute('INSERT INTO employee(fname, lname, password, email) VALUES (%s, %s, %s, %s)', (f_name, l_name, hashed_password, email))
            mysql.connection.commit()
            cur.close()
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
    msg = ''
    if 'loggedin' in session:
        if request.method == "POST":
            phone = request.form['phone']
            dob = request.form['dob']
            state = request.form['state']
            city = request.form['city']

            # Image upload================
            image = request.files["pic"]
            if image.filename:
                image.save(os.path.join(os.getcwd()+'/static/upload_images', image.filename))

            # update database==================
            cur = mysql.connection.cursor()
            cur.execute("UPDATE employee SET phone=%s, dob=%s, state=%s, city=%s, image=%s  WHERE email=%s ", (phone, dob, state, city, image.filename, session['email']))
            msg = 'Profile successfully updated'
            mysql.connection.commit()
            cur.close()

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM employee WHERE email = %s', [session['email']])
        account = cur.fetchone()
        return render_template('profile.html', fname=account[0], lname=account[1], phone=account[2], email=account[3], dob=account[5], state=account[6], city=account[7], user_image=account[8], msg=msg)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

