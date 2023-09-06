from flask import Flask, render_template, redirect, request, url_for

# create instance of flask and assign it to "app"
app = Flask(__name__)


# create a route
@app.route("/")
@app.route("/index")
def index():
    first_name = "Marina"
    return render_template("index.html", first_name=first_name)


# localhost:5000/user/Marina
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", user_name=name)


@app.route("/journal")
def journal():
    return render_template("journal.html")


@app.route("/news")
def news():
    return render_template("news.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/logout")
def logout():
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/register_page")
def register_page():
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
