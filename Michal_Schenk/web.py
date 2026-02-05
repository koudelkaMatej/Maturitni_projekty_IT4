import flask
from flask import request, redirect, jsonify, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from db_handling import UserModel as User
import db_handling


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-this"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gradproj.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login" # type: ignore

@login_manager.user_loader
def load_user(user_id):
    return db_handling.query_rows(db_handling.UserModel, {'id': int(user_id)})[0]

@app.route('/')
def home():
    return render_template('index.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user = User(username=request.form['username'], email=request.form['email'])
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = db_handling.query_rows(db_handling.UserModel, {'username': request.form['username']})
        user = user[0] if user else None
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')
        else:
            return "Invalid credentials", 401
    return render_template('login.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/leaderboard')
def leaderboard():
    sessions = db_handling.query_rows(db_handling.GameSessionModel, include=['user'])
    print(sessions)
    return render_template('leaderboard.html', sessions=sessions)

@app.route('/dashboard')
@login_required
def dashboard():
    sessions = db_handling.query_rows(db_handling.GameSessionModel, {'user_id': current_user.id}, include=['user'])
    print(sessions)
    return render_template('dashboard.html', sessions=sessions, user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == "POST":
        user = current_user
        if user.check_password(request.form['current_password']):
            user.set_password(request.form['new_password'])
            db.session.commit()
            return redirect('/profile')
        else:
            return "Current password is incorrect", 401
    return render_template('change_password.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)