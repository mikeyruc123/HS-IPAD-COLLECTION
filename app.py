from flask import Flask, render_template, redirect, session, request, g, send_file
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
            return redirect("/student/"+request.form["studentid"])
    else:
        return redirect("/login")

@app.route("/list") #check credentials; list all ipads given a filter
def ipad_list():
    return render_template("temp.html")

@app.route("/student/<int(min=0, max=65535):id>", methods=['GET', 'POST']) #check credentials first and if student exists; return login page or invalid student page
def student_id(id):
    if request.method == "GET":
        if check_cred():
            cur = get_db().cursor()
            cur.execute(f"SELECT * FROM students WHERE id = '{id}'")
            name = cur.fetchall()
            name = name[0]
            ret_check = ""
            crack_check = ""
            char_check = ""
            if (name[2]): ret_check = "checked"
            if (name[3]): crack_check = "checked"
            if (name[4]): char_check = "checked"
            return render_template("studentid.html", var_id=id, var_name=name[1], var_returned=name[2], var_cracked=name[3], var_charger=name[4],
            var_ret_check=ret_check, var_crack_check=crack_check, var_char_check=char_check)
        else:
            return redirect("/login")
    elif request.method == "POST":
        cur = get_db().cursor()
        ret_check = ""
        crack_check = ""
        char_check = ""
        if request.form.get("var_name") != "":
            cur.execute(f"UPDATE students SET name = '{request.form['var_name']}' WHERE id = '{id}'")

        if request.form.get("var_returned") != None:
            cur.execute(f"UPDATE students SET returned = '{request.form['var_returned']}' WHERE id = '{id}'")
            ret_check = "checked"
        else:
            cur.execute(f"UPDATE students SET returned = 0 WHERE id = '{id}'")

        if request.form.get("var_cracked") != None:
            cur.execute(f"UPDATE students SET cracked = '{request.form['var_cracked']}' WHERE id = '{id}'")
            crack_check = "checked"
        else:
            cur.execute(f"UPDATE students SET cracked = 0 WHERE id = '{id}'")

        if request.form.get("var_charger") != None:
            cur.execute(f"UPDATE students SET charger = '{request.form['var_charger']}' WHERE id = '{id}'")
            char_check = "checked"
        else:
            cur.execute(f"UPDATE students SET charger = 0 WHERE id = '{id}'")

        get_db().commit()
        cur.execute(f"SELECT * FROM students WHERE id = '{id}'")
        name = cur.fetchall()
        name = name[0]
        return render_template("studentid.html", var_id=id, var_name=name[1], var_returned=name[2], var_cracked=name[3], var_charger=name[4],
        var_ret_check=ret_check, var_crack_check=crack_check, var_char_check=char_check)

@app.route("/favicon.ico")
def icon():
    return send_file("static/favicon.ico")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
#@app.route("/<route>") #catch all; redirects any invalid routes to the root
def catch_all(path):
    print("Requested " + path)
    return redirect("/")

def check_cred(): #login checker; see if there is a username entry for the current session; implies successful login
    if "username" in session:
        return True
    else:
        return False