from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import SECRET_KEY
from control.loginC import LoginController
from control.adminAccountC import AdminAccountController
from control.adminProfileC import AdminProfileController

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_controller = LoginController()
admin_account_controller = AdminAccountController()
admin_profile_controller = AdminProfileController()

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
            session["role"] = result["role"]

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

'''
---------- Admin Page ----------
'''

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    keyword = request.args.get("keyword", "").strip()

    if keyword:
        accounts = admin_account_controller.search_accounts(keyword)
    else:
        accounts = admin_account_controller.get_all_accounts()

    return render_template(
        "admin_dashboard.html",
        user_name=session.get("full_name"),
        accounts=accounts,
        keyword=keyword
    )


@app.route("/admin/accounts/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_account():
    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        role = request.form.get("role", "")
        status = request.form.get("status", "")

        result = admin_account_controller.create_account(
            full_name, username, email, password, role, status
        )

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin_dashboard"))

        flash(result["message"], "danger")

    return render_template(
        "admin_account_form.html",
        form_mode="create",
        account=None
    )


@app.route("/admin/accounts/<int:account_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_account(account_id):
    account = admin_account_controller.get_account_by_id(account_id)

    if not account:
        flash("Account not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        role = request.form.get("role", "")
        status = request.form.get("status", "")
        new_password = request.form.get("new_password", "")

        result = admin_account_controller.update_account(
            account_id, full_name, username, email, role, status, new_password
        )

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin_dashboard"))

        flash(result["message"], "danger")

    return render_template(
        "admin_account_form.html",
        form_mode="edit",
        account=account
    )


@app.route("/admin/accounts/<int:account_id>/suspend", methods=["POST"])
@login_required
@role_required("admin")
def suspend_account(account_id):
    result = admin_account_controller.suspend_account(account_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/profiles")
@login_required
@role_required("admin")
def admin_profiles():
    keyword = request.args.get("keyword", "").strip()

    if keyword:
        profiles = admin_profile_controller.search_profiles(keyword)
    else:
        profiles = admin_profile_controller.get_all_profiles()

    return render_template(
        "admin_profiles.html",
        profiles=profiles,
        keyword=keyword
    )


@app.route("/admin/profiles/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_profile():
    available_accounts = admin_profile_controller.get_accounts_without_profiles()

    if request.method == "POST":
        account_id = request.form.get("account_id", "").strip()
        role = request.form.get("role", "").strip()

        result = admin_profile_controller.create_profile(account_id, role)

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin_profiles"))

        flash(result["message"], "danger")

    return render_template(
        "admin_profile_form.html",
        form_mode="create",
        profile=None,
        available_accounts=available_accounts
    )


@app.route("/admin/profiles/<int:profile_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_profile(profile_id):
    profile = admin_profile_controller.get_profile_by_id(profile_id)

    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for("admin_profiles"))

    if request.method == "POST":
        role = request.form.get("role", "").strip()

        result = admin_profile_controller.update_profile(profile_id, role)

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin_profiles"))

        flash(result["message"], "danger")

    return render_template(
        "admin_profile_form.html",
        form_mode="edit",
        profile=profile,
        available_accounts=[]
    )


@app.route("/admin/profiles/<int:profile_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_profile(profile_id):
    result = admin_profile_controller.delete_profile(profile_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_profiles"))


@app.route("/admin/profiles")
@login_required
@role_required("admin")
def admin_profiles():
    keyword = request.args.get("keyword", "").strip()

    if keyword:
        profiles = admin_profile_controller.search_profiles(keyword)
    else:
        profiles = admin_profile_controller.get_all_profiles()

    return render_template(
        "admin_profiles.html",
        profiles=profiles,
        keyword=keyword
    )


@app.route("/admin/profiles/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_profile():
    available_accounts = admin_profile_controller.get_accounts_without_profiles()

    if request.method == "POST":
        account_id = request.form.get("account_id", "").strip()
        role = request.form.get("role", "").strip()

        result = admin_profile_controller.create_profile(account_id, role)

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin_profiles"))

        flash(result["message"], "danger")

    return render_template(
        "admin_profile_form.html",
        form_mode="create",
        profile=None,
        available_accounts=available_accounts
    )


@app.route("/admin/profiles/<int:profile_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_profile(profile_id):
    profile = admin_profile_controller.get_profile_by_id(profile_id)

    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for("admin_profiles"))

    if request.method == "POST":
        role = request.form.get("role", "").strip()

        result = admin_profile_controller.update_profile(profile_id, role)

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin_profiles"))

        flash(result["message"], "danger")

    return render_template(
        "admin_profile_form.html",
        form_mode="edit",
        profile=profile,
        available_accounts=[]
    )


@app.route("/admin/profiles/<int:profile_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_profile(profile_id):
    result = admin_profile_controller.delete_profile(profile_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_profiles"))

'''
---------- Fundraiser Page ----------
'''

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