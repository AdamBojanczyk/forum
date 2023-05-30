from flask import Flask, redirect, render_template, request, make_response, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager,login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'fdkjlsajfsljklj3lk423jlkjfdslkjfljklds'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(30), nullable = False)
    lastname = db.Column(db.String(30), nullable = False)
    username = db.Column(db.String(30), nullable = False, unique=True)
    email = db.Column(db.String(30), nullable = False)
    password = db.Column(db.String(30), nullable = False)

    def __repr__(self):
        return f'<User {self.id}, {self.name}, {self.lastName}, {self.username}, {self.email}, {self.password}>'
    
class Posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.String(30), nullable = False)
    value = db.Column(db.String(500), nullable = False)
    writer = db.Column(db.String(50), nullable = False)
    date = db.Column(db.DateTime(), server_default=func.now())




class RegisterForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=3, max=30)], render_kw={"placeholder": "Imię"})
    surname = StringField(validators=[InputRequired(), Length(min=3, max=30)], render_kw={"placeholder": "Nazwisko"})
    username = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Nazwa Użytkownika"})
    email = EmailField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Hasło"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError("That username already exists. Please choose a different one.")
        
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Nazwa Użytkownika"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Hasło"})

    submit = SubmitField("Login")



@app.route("/")
def index():
    if not 'user' in request.cookies:
        return redirect("/login")
    else:
        name = request.cookies.get('user')
        posts = Posts.query.order_by(desc(Posts.date)).all()
        return render_template('index.html', username = name, posts = posts)

@app.route("/login", methods=['POST', 'GET'])
def login():
    # 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)

                username = request.form['username']
                resp = make_response(redirect('/'))
                resp.set_cookie('user', username)
                return resp
            
    return render_template('login.html', form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
    # 
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        newUser = User(name = form.name.data, lastname = form.surname.data, username = form.username.data, email = form.email.data, password = hashed_password)

        try:
            db.session.add(newUser)
            db.session.commit()
            
            return redirect(url_for('login'))
        except:
            return 'There was an issue registering you'
    else:
        return render_template('register.html', form=form)
    
@app.route("/write_post", methods=['POST', 'GET'])
def write_post():
    if request.method == 'POST':
        title = request.form['title']
        value = request.form['value']
        if not 'user' in request.cookies:
            return redirect("/")
        else:
            writer = request.cookies.get('user')

        newPost = Posts(title = title, value = value, writer = writer)

        try:
            db.session.add(newPost)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your post'
    else:
        return render_template('write_post.html')
    
@app.route("/logout", methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    resp = make_response(redirect('/login'))
    resp.delete_cookie('user')
    return resp



@app.route("/users")
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route("/like")
def like():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)