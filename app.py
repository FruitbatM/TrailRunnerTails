from flask import Flask, render_template

# create instance of flask and assign it to "app"
app = Flask(__name__)


# create a route
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


# localhost:5000/user/Marina
@app.route("/user/<name>")
def user(name):
    return "<h1>Hello World! {}</h1>".format(name)
