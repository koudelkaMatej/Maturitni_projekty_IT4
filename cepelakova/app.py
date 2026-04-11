from flask import Flask, render_template, request, redirect, session
from databaze import (register_user, get_user_by_username, get_all_scores, delete_score,
init_db, get_all_users, delete_user, get_scores_by_difficulty, get_user_achievements, get_all_achievements, get_user_stats)
app = Flask(__name__)
app.secret_key = "secret123"

init_db()

@app.route("/profile")
def profile():
    if not session.get("user"):
        return redirect("/login")
    user_id = session["user_id"]
    achievements = get_user_achievements(user_id)
    all_achievements = get_all_achievements()
    return render_template("profile.html", 
                           achievements=achievements, 
                           all=all_achievements,
                           username=session["user"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user_by_username(username)

        if user is None:
            error = "User does not exist!"
        elif user["password"] != password:
            error = "Wrong password!"
        else:
            session["user"] = user["username"]
            session["user_id"] = user["id"] 
            session["role"] = user["role"]
            return redirect("/")

    return render_template("login.html", error=error)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]

        if password != password2:
            error = "Passwords do not match"
            return render_template("register.html", error=error)

    
        if register_user(username, password):
            return redirect("/login")
        else:
            error = "Username already exists"

    return render_template("register.html", error=error)

@app.route("/leaderboard")
def leaderboard():
    if not session.get("user"):
        return "First login!"

    data = get_all_scores()
    return render_template("leaderboard.html", data=data)

@app.route("/leaderboard/filter", methods=["GET"])
def leaderboard_filter():
    if not session.get("user"):
        return redirect("/login")
    
    difficulty = request.args.get("difficulty")
    data = get_scores_by_difficulty(difficulty)
    return render_template("leaderboard_filter.html", data=data, selected=difficulty)

@app.route("/stats")
def stats():
    if not session.get("user"):
        return redirect("/login")
    stats_data = get_user_stats()
    return render_template("stats.html", stats=stats_data)
    
    difficulty = request.args.get("difficulty")
    data = get_scores_by_difficulty(difficulty)
    return render_template("leaderboard_filter.html", data=data, selected=difficulty)

@app.route("/delete_score/<int:id>")
def delete_score_route(id):
    if session.get("role") != "admin":
        return "Access denied"

    delete_score(id)
    return redirect("/leaderboard")

@app.route("/users")
def users_list():
    if session.get("role") != "admin":
        return "Access denied", 403
    users = get_all_users()
    return render_template("users.html", users=users)

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if not session.get("user"):
        return redirect("/login")
    
    error = None
    success = None
    
    if request.method == "POST":
        old = request.form["old_password"]
        new = request.form["new_password"]
        confirm = request.form["confirm_password"]
        
        user = get_user_by_username(session["user"])
        if user["password"] != old:
            error = "Staré heslo není správné"
        elif new != confirm:
            error = "Nová hesla se neshodují"
        elif len(new) < 3:
            error = "Nové heslo musí mít alespoň 3 znaky"
        else:
            change_password(session["user_id"], new)
            success = "Heslo bylo změněno"
    
    return render_template("change_password.html", error=error, success=success)

@app.route("/delete_user/<int:user_id>")
def delete_user_route(user_id):
    if session.get("role") != "admin":
        return "Access denied", 403
    
    if user_id == session.get("user_id"):
        return "Nemůžeš smazat sám sebe!", 400
    
    delete_user(user_id)
    return redirect("/users")

if __name__ == "__main__":
    app.run(debug=True)