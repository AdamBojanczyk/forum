from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    lastName = db.Column(db.String(30), nullable = False)
    username = db.Column(db.String(30), nullable = False)
    dateOfBirth = db.Column(db.Date, nullable = False)
    email = db.Column(db.String(30), nullable = False)
    password = db.Column(db.String(30), nullable = False)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

    return render_template('login.html')

@app.route("/register")
def register():
    if request.method == 'POST':
        name = request.form['name']
        lastName = request.form['lastName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        newUser = User(name = name, lastName = lastName, username = username, email = email, password = password)

        try:
            db.session.add(newUser)
            db.session.commit()
            return redirect('index.html')
        except:
            return 'There was an issue registering you'
    else:
        return render_template('register.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)