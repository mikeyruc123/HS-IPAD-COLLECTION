from flask import Flask, render_template, redirect, session, request, g
import secrets, sqlite3

app = Flask(__name__)
app.secret_key = secrets.token_hex() #change out later

S_DB = "data/students.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(S_DB)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/") #root directory routing; return login page or dashboard if session / cookie exists
def root():
    if check_cred():
        return redirect("/dashboard")
    else:
        return redirect("/login")

@app.route("/login", methods=['GET', 'POST']) #login screen; redirect if session / cookie exists
def login():
    if check_cred():
        return redirect("/dashboard")
    else:
        if request.method == "GET":
            return render_template("login.html")
        elif request.method == "POST":
            session["username"] = request.form["username"]
            return redirect("/dashboard")

@app.route("/logout") #logout; no webpage, just logout and redirect to login
def logout():
    if check_cred():
        session.pop('username', None)
    return redirect("/login")

@app.route("/dashboard", methods=["GET", "POST"]) #dashboard routing; return login page if no session exists
def dashboard():
    if check_cred():
        if request.method == "GET":
            return render_template("dashboard.html", var_username=session["username"])
        else:
            return redirect("/student"+request.form["studentid"])
    else:
        return redirect("/login")

@app.route("/list") #check credentials; list all ipads given a filter
def ipad_list():
    return render_template("temp.html")

@app.route("/student<int(min=0, max=65535):id>") #check credentials first and if student exists; return login page or invalid student page
def student_id(id):
    if check_cred():
        cur = get_db().cursor()
        return render_template("studentid.html", var_id=cur.execute("SELECT * FROM students"))
    else:
        return redirect("/login")

#@app.route("/<route>") #catch all; redirects any invalid routes to the root
#def catch_all(route):
#    print("Requested " + route)
#    return redirect("/")

def check_cred(): #login checker; see if there is a username entry for the current session; implies successful login
    if "username" in session:
        return True
    else:
        return False