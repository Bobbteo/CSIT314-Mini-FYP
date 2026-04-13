from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import SECRET_KEY
from control.loginC import LoginController

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_controller = LoginController()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "account_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "account_id" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))

            if session.get("role") != required_role:
                flash("You are not authorized to access that page.", "danger")
                return redirect(url_for("dashboard_redirect"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route("/")
def home():
    if "account_id" in session:
        return redirect(url_for("dashboard_redirect"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username_or_email", "").strip()
        password = request.form.get("password", "").strip()

        result = login_controller.authenticate(username_or_email, password)

        if result["success"]:
            account = result["account"]
            session["account_id"] = account.account_id
            session["full_name"] = account.full_name
            session["username"] = account.username
            session["role"] = account.role

            flash(result["message"], "success")
            return redirect(url_for("dashboard_redirect"))

        flash(result["message"], "danger")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard_redirect():
    role = session.get("role")
    print("DEBUG role from session =", role)

    dashboard_route = login_controller.get_dashboard_route(role)
    print("DEBUG dashboard route =", dashboard_route)

    if dashboard_route:
        return redirect(url_for(dashboard_route))

    flash(f"Unknown user role: {role}", "danger")
    return redirect(url_for("login"))


@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    return render_template("admin_dashboard.html", user_name=session.get("full_name"))


@app.route("/fundraiser")
@login_required
@role_required("fundraiser")
def fundraiser_dashboard():
    return render_template("fundraiser_dashboard.html", user_name=session.get("full_name"))


@app.route("/doner")
@login_required
@role_required("doner")
def doner_dashboard():
    return render_template("doner_dashboard.html", user_name=session.get("full_name"))


@app.route("/manager")
@login_required
@role_required("manager")
def manager_dashboard():
    return render_template("manager_dashboard.html", user_name=session.get("full_name"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)