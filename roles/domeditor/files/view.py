from flask import Flask, session, redirect, request, render_template, url_for, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import model

app = Flask(__name__)
app.secret_key="SetSecretKeyHere"
logman = LoginManager()
logman.init_app(app)


@logman.user_loader
def load_user(user_id):
    user = model.get_user(user_id)
    return user


@app.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    username = auth.username
    password = auth.password
    password_correct = model.is_password_valid(username, password)

    result = {}

    if password_correct:
        user = model.get_user(username)
        user.is_active = True
        user.is_authenticated = True
        login_user(user)
        url = url_for("main_page")
        result["state"] = "succeeded"
        result["url"] = url
    else:
        result["state"] = "failed"

    return jsonify(result)


@app.route("/createuser", methods=["POST"])
def create_user():
    data = request.get_json()
    new_username = data.get("newUsername")
    new_password = data.get("newPassword")
    confirmed_password = data.get("confirmedPassword")

    existing_user = model.get_user(new_username)
    if existing_user:
        msg = "User already exists"
    elif new_password == confirmed_password:
        msg = model.create_user(new_username, new_password)
        model.initialize_dom_numbers(new_username)
    else:
        msg = "Passwords do not match"
    return msg


@app.route("/logout")
def logout():
    username = current_user.username
    model.set_authenticate(username, False)
    logout_user()
    return redirect("/static/login.html")


@app.route("/mainpage")
def main_page():
    if current_user.is_anonymous:
        return redirect("/static/login.html")
    else:
        return render_template("mainpage.html")


@app.route("/")
def index():
    return redirect("/static/login.html")


@app.route("/usercreds", methods=["GET"])
def get_user_creds():
    user_id = session.get("user_id")
    password = model.get_user(user_id).password
    credentials = {"username": user_id,
                   "password": password}
    return jsonify(credentials)


@app.route("/savedomnum", methods=["POST"])
def save_dom_num():
    auth = request.authorization
    json_data = request.get_json()
    user = auth.username
    pw = auth.password
    num = json_data.get("number")
    person = json_data.get("person")
    action = json_data.get("action")

    if model.is_password_valid(user, pw, prehashed=True):
        result = model.update_dom_num(user, num, person, action)
        return result
    else:
        return "FAILED"

@app.route("/revert/<num>", methods=["GET"])
def revert_number(num):
    auth = request.authorization
    uname = auth.username
    pw = auth.password

    if model.is_password_valid(uname, pw, prehashed=True):
        dom_num = model.get_dom_num(uname, num)
        return jsonify(dom_num)
    else:
        abort(401)


if __name__ == '__main__':
    app.run(debug=True)
