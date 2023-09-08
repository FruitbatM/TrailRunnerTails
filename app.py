from flask import (
    Flask, render_template, redirect, session,
    request, url_for, flash)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

if os.path.exists("env.py"):
    import env

# Create instance of flask and assign it to "app"
app = Flask(__name__)

# Gab the environment variables
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# mongodb name is 'trail_runner_tails'
userData = mongo.db.users

if os.environ.get("DEBUG") == 'True':
    app.debug = True
else:
    app.debug = False


# Create a route
@app.route("/", methods=['GET', 'POST'])
def index():
    first_name = "Marina"
    return render_template("index.html", first_name=first_name)


# localhost:5000/user/Marina
@app.route("/user/add", )
def user(name):
    return render_template("user.html", user_name=name)


@app.route("/journal")
def journal():
    return render_template("journal/journal.html")


@app.route("/news")
def news():
    return render_template("news.html")


@app.route("/about")
def about():
    return render_template("about.html")


# User login
@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in function which checks that username and password
    match values in the database
    """
    if request.method == "POST":
        # Check if username exists in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"],
                    request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(
                    url_for("profile", username=session["user"]))

            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been successfully logged out")
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username with this name already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "first_name": request.form.get("first_name").capitalize(),
            "last_name": request.form.get("last_name").capitalize(),
            "is_admin": False
        }
        mongo.db.users.insert_one(register)

    return render_template("register.html")


# 404 error
@app.errorhandler(404)
def error_404(error):
    '''
    Handles 404 error (Page not found)
    '''
    return render_template("error/404.html", error=True,
                           title="Page not found"), 404


# 500 error
@app.errorhandler(500)
def error_500(error):
    '''
    Handles 500 error (Internal Server Error)
    '''
    return render_template("error/500.html", error=True,
                           title="Internal Server Error"), 500


@app.route('/linkedin')
def linkedin():
    """
    Function to load Linkedin
    """
    return redirect("https://www.linkedin.com")


@app.route('/facebook')
def facebook():
    """
    Function to load Facebook
    """
    return redirect("https://www.facebook.com")


@app.route('/github')
def github():
    """
    Function to load Github
    """
    return redirect("https://github.com")


@app.route('/instagram')
def instagram():
    """
    Function to load Instagram
    """
    return redirect("https://www.instagram.com")


@app.route('/youtube')
def youtube():
    """
    Function to load Youtube
    """
    return redirect("https://www.youtube.com/")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
