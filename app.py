from flask import (
    Flask, render_template, redirect, session,
    request, url_for, flash)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_ckeditor import CKEditor, CKEditorField
import os

if os.path.exists("env.py"):
    import env

# Create instance of flask and assign it to "app"
app = Flask(__name__)
app.config['SECRET_KEY'] = "this is my secret crf key"


# Add CKEditor
app.config['CKEDITOR_SERVE_LOCAL'] = True
ckeditor = CKEditor(app)

# Gab the environment variables
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# mongodb name is 'trailrunnertails_db'
userData = mongo.db.users
journalData = mongo.db.journal

if os.environ.get("DEBUG") == 'True':
    app.debug = True
else:
    app.debug = False


# Create a Form class
class JournalForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    credit = StringField("Credit", validators=[DataRequired()])
    published_date = StringField("Date", validators=[DataRequired()])
    image1 = StringField("Image 1")
    paragraph_1 = CKEditorField("Paragraph 1", validators=[DataRequired()])
    paragraph_2 = CKEditorField("Paragraph 2", validators=[DataRequired()])
    image2 = StringField("Image 2")
    paragraph_3 = CKEditorField("Paragraph 3")
    paragraph_4 = CKEditorField("Paragraph 4")
    submit = SubmitField("Submit")


# Create a route
@app.route("/", methods=['GET', 'POST'])
def index():
    # Fetch the first three journal posts from the MongoDB collection
    journals = list(journalData.find().limit(3))
    return render_template("index.html", journals=journals)


@app.route("/journal")
def journal():
    """
    Viewing Journal Posts
    """
    # Fetch all journal posts from the MongoDB collection
    journals = list(journalData.find())

    return render_template("journal/journal.html", journals=journals, user_is_authorized_to_delete=user_is_authorized_to_delete)


@app.route("/journal_post/<post_id>")
def journal_post(post_id):
    """
    Display a single journal post.
    """
    # Retrieve the journal post from the database using the ObjectId
    post = journalData.find_one({"_id": ObjectId(post_id)})
    if not post:
        flash("Journal post not found.")
        return redirect(url_for("journal"))

    return render_template("journal/journal_post.html", post=post)


@app.route("/add_journal", methods=["GET", "POST"])
def add_journal():
    """
    Filling in the add journal form and handling form submission.
    """
    form = JournalForm()

    # Automatically set the date to the current date
    form.published_date.data = datetime.now().strftime("%d-%m-%Y")

    # Validate Form
    if form.validate_on_submit():
        title = form.title.data
        credit = form.credit.data
        published_date = form.published_date.data
        image1 = form.image1.data
        paragraph_1 = form.paragraph_1.data
        paragraph_2 = form.paragraph_2.data
        image2 = form.image2.data
        paragraph_3 = form.paragraph_3.data
        paragraph_4 = form.paragraph_4.data

        # Create a new journal post document
        new_journal = {
            "title": title,
            "credit": credit,
            "published_date": published_date,
            "image1": image1,
            "image2": image2,
            "paragraph_1": paragraph_1,
            "paragraph_2": paragraph_2,
            "paragraph_3": paragraph_3,
            "paragraph_4": paragraph_4,
        }

        # Insert the new journal post into the MongoDB collection
        journalData.insert_one(new_journal)

        # Redirect to the journal page after adding the post
        flash("Journal post added successfully")
        return redirect(url_for("journal"))

    return render_template("journal/add_journal.html", form=form)


@app.route("/edit_journal/<post_id>", methods=["GET", "POST"])
def edit_journal(post_id):
    """
    Edit journal post.
    """
    # Retrieve the journal post from the database using the ObjectId
    post = journalData.find_one({"_id": ObjectId(post_id)})
    if not post:
        flash("Journal post not found.")
        return redirect(url_for("journal"))

    # Create a form and pre-fill it with the existing data
    form = JournalForm(obj=post)

    if form.validate_on_submit():
        # Update the journal post data
        post["title"] = form.title.data
        post["credit"] = form.credit.data
        post["published_date"] = form.published_date.data
        post["image1"] = form.image1.data
        post["paragraph_1"] = form.paragraph_1.data
        post["paragraph_2"] = form.paragraph_2.data
        post["image2"] = form.image2.data
        post["paragraph_3"] = form.paragraph_3.data
        post["paragraph_4"] = form.paragraph_4.data

        # Update the post in the database
        journalData.update({"_id": ObjectId(post_id)}, post)

        flash("Journal post updated successfully")
        return redirect(url_for("journal_post", post_id=post_id))

    return render_template("journal/edit_journal.html", form=form, post=post, post_id=post_id)


@app.route("/delete_journal/<post_id>", methods=["GET", "POST"])
def delete_journal(post_id):
    """
    Delete journal post.
    """
    # Retrieve the journal post from the database using the post_id
    post = journalData.find_one({"_id": ObjectId(post_id)})

    if not post:
        flash("Journal post not found.")
        return redirect(url_for("journal"))

    # Check if the user is authorized to delete the post (e.g., admin check)
    if not user_is_authorized_to_delete():
        flash("You are not authorized to delete this journal post.")
        return redirect(url_for("journal"))

    # Delete the journal post from the database
    journalData.delete_one({"_id": ObjectId(post_id)})
    flash("Journal post deleted successfully.")
    return redirect(url_for("journal"))


def user_is_authorized_to_delete():
    # Check if the user is authenticated and has permission to delete
    if session.get("user") == "admin":
        return True
    else:
        return False


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
                # Set the user's role in the session
                session["role"] = "admin" if existing_user.get(
                    "is_admin") else "user"
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for("index"))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("journal/journal.html")


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been successfully logged out")
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    return render_template("admin.html", users=userData.find())


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
