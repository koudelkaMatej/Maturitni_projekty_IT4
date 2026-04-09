import flask
from flask import request, redirect, jsonify, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from db_handling import UserModel as User
import db_handling
import uuid
import datetime
import logger
log = logger.get_logger("web")



app = flask.Flask(__name__)
app = flask.Flask(__name__, static_url_path='')
app.config["SECRET_KEY"] = "dev-secret-change-this"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ditr.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.login_view = "login" # type: ignore


@login_manager.user_loader
def load_user(user_id:int):
	"""Load a user instance for the current login session. This is used by Flask-Login to restore authenticated users between requests.

	Args:
		user_id (int): The primary key of the user to load from the database.

	Returns:
		db_handling.UserModel | None: The loaded user model instance if found, otherwise None.
	"""
	user = db.session.query(db_handling.UserModel).filter_by(id=user_id).first()
	log.info(f"LOADED USER: {user}")
	return user


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
		log.info(f"NEW USER: {user}")
		return redirect('/login')
	return render_template('register.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		user = db.session.query(db_handling.UserModel).filter_by(username=request.form['username']).first()
		if user and user.check_password(request.form['password']):
			if user.banned:
				log.info("REFUSE LOGIN - BANNED")
				return "USER BANNED"
			login_user(user)
			log.info("ACCEPT LOGIN")
			return redirect('/')
		else:
			log.info("REFUSE LOGIN - INVALID CREDENTIALS")
			return "Invalid credentials", 401
	return render_template('login.html')




@app.route('/logout')
@login_required
def logout():
	logout_user()
	log.info("LOG OUT")
	return redirect('/')


@app.route('/profile')
@login_required
def profile():
	unsorted_sessions = db.session.query(db_handling.GameSessionModel).filter_by(user_id=current_user.id).all()
	sorted_sessions = sorted(unsorted_sessions, key=lambda x: (-x.level_reached, -x.score))
	return render_template('profile.html', user=current_user, sessions=sorted_sessions)




@app.route('/leaderboard')
def leaderboard():
	if current_user.role == "admin":
		unsorted_sessions = db.session.query(db_handling.GameSessionModel).all()
	else:
		unsorted_sessions = db.session.query(db_handling.GameSessionModel).filter_by(invalid=0).all()
	sorted_sessions = sorted(unsorted_sessions, key=lambda x: (-x.level_reached, -x.score))
	return render_template('leaderboard.html', sessions=sorted_sessions, user=current_user)



@app.route('/dashboard')
@login_required
def dashboard():
	unsorted_sessions = db.session.query(db_handling.GameSessionModel).filter_by(user_id=current_user.id).all()
	sorted_sessions = sorted(unsorted_sessions, key=lambda x: (-x.level_reached, -x.score))
	return render_template('dashboard.html', sessions=sorted_sessions, user=current_user)


@app.route('/about')
def about():
	return render_template('about.html', user=current_user)


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
	if request.method == "POST":
		user = current_user
		if user.check_password(request.form['current_password']):
			user.set_password(request.form['new_password'])
			db.session.commit()
			log.info(f"CHANGED PASSWORD: {user}")
			return redirect('/profile')
		else:
			log.info(f"WRONG PASSWORD: {user}")
			return "Current password is incorrect", 401
	return render_template('change_password.html')


@app.route('/editor')
@login_required
def db_editor():
	if current_user.role == "admin":
		return render_template('editor.html', user=current_user)
	else:
		return flask.redirect("/")
	
@app.route('/api/users')
@login_required
def api_users():
	if current_user.role == "admin":
		users = db.session.query(db_handling.UserModel).all()
		return render_template('frags/user_frag.html', users=users)
	else:
		return flask.redirect("/")
	
@app.route('/api/game-sessions')
@login_required
def api_game_sessions():
	if current_user.role == "admin":
		games = db.session.query(db_handling.GameSessionModel).all()
		return render_template('frags/game_session_frag.html', games=games)
	else:
		return flask.redirect("/")


@app.route('/api/invalidate/<int:id>', methods=['GET', 'POST'])
def api_invalidate(id:int):
	"""Invalidate a specific game session by its identifier. This endpoint is restricted to admin users and marks the session as invalid when called via POST.

	Args:
		id (int): The unique identifier of the game session to invalidate.

	Returns:
		tuple[dict, int] | tuple[dict, int]: An empty JSON response with HTTP 200 when the request is processed, or an empty JSON response with HTTP 404 if the session does not exist for a valid admin POST request.
	"""
	if request.method == 'POST':
		if current_user.role == "admin":
			run = db.session.query(db_handling.GameSessionModel).filter_by(id=id).first()
			if not run:
				return {}, 404
			run.invalid = 1
			log.debug(f"INVALIDATED GAME SESSION.ID {run.id} BY {current_user.username}")
			db.session.commit()
	return {}, 200

@app.route('/api/delete/user/<int:id>', methods=['GET', 'POST'])
def api_delete_user(id):
	"""Delete a user and all of their game sessions by identifier. This endpoint is restricted to admin users and removes both the user record and any associated sessions when called via POST.

	Args:
		id (int): The unique identifier of the user to delete.

	Returns:
		dict | tuple[dict, int]: An empty JSON object with HTTP 200 on success or for non-POST/non-admin access, or an empty JSON object with HTTP 404 if the user does not exist for a valid admin POST request.
	"""
	if request.method == 'POST':
		if current_user.role == "admin":
			user = db.session.query(db_handling.UserModel).filter_by(id=id).first()
			if not user:
				return {}, 404
			games = db.session.query(db_handling.GameSessionModel).filter_by(user_id=user.id).all()

			db.session.delete(user)
			log.debug(f"DELETED USER.ID {user.id} BY {current_user.username}")
			for game in games:
				db.session.delete(game)
				log.debug(f"DELETED GAME SESSION.ID {game.id} BY {current_user.username}")
			db.session.commit()
			
			
	return {}


@app.route('/api/update/user/<int:id>', methods=['GET', 'POST'])
@login_required
def api_update_user(id):
	"""Update an existing user's details by identifier. This endpoint is restricted to admin users and applies form-provided changes to the selected user when called via POST.

	Args:
		id (int): The unique identifier of the user to update.

	Returns:
		dict | tuple[dict, int]: An empty JSON object with HTTP 200 when the update is processed or for non-POST/non-admin access, or an empty JSON object with HTTP 404 if the user does not exist for a valid admin POST request.
	"""
	if request.method == 'POST':
		if current_user.role == "admin":
			user = db.session.query(db_handling.UserModel).filter_by(id=id).first()
			if not user:
				return {}, 404
			data = request.form
			user.username = data.get("username")
			user.email = data.get("email")
			if not data.get("password_hash", "scrypt:").startswith("scrypt:"):
				user.password_hash = generate_password_hash(str(data.get("password_hash")))
			user.created_at = datetime.datetime.fromisoformat(str(data.get("created_at")))
			user.prefered_scheme = data.get("scheme")
			user.role = data.get("role")
			user.banned = data.get("banned")
			db.session.commit()	
			log.debug(f"UPDATED USER.ID {user.id}: {user}")
	return {}

@app.route('/api/update/game-session/<int:id>', methods=['GET', 'POST'])
@login_required
def api_update_game_session(id):
	"""Update the invalidation status of a specific game session by identifier. This endpoint is restricted to admin users and applies form-provided changes when called via POST.

	Args:
		id (int): The unique identifier of the game session to update.

	Returns:
		dict | tuple[dict, int]: An empty JSON object with HTTP 200 when the update is processed or for non-POST/non-admin access, or an empty JSON object with HTTP 404 if the game session does not exist for a valid admin POST request.
	"""
	if request.method == 'POST':
		if current_user.role == "admin":
			game = db.session.query(db_handling.GameSessionModel).filter_by(id=id).first()
			if not game:
				return {}, 404
			data = request.form
			game.invalid = data.get("invalid")
			db.session.commit()	
			log.debug(f"UPDATED GAME SESSION.ID {game.id}: {game}")
	return {}




@app.before_request
def log_request_info():
	"""Log basic information about the incoming request for observability. This helper builds a simple route identifier and associates it with the current user for debugging and auditing.

	The logger records the resolved endpoint name and any view parameters, excluding static file requests. This allows tracking which authenticated or anonymous user accessed which route pattern.
	"""
	endpoint = flask.request.endpoint or "unknown"
	if endpoint != "static":
		view_params = flask.request.view_args
		
		if view_params:
			param_string = ".".join(str(v) for v in view_params.values())
			log_name = f"route.{endpoint}.{param_string}"
		else:
			log_name = f"route.{endpoint}"

		log.info(f"{current_user} - {log_name}")

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)

