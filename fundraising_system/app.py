from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import SECRET_KEY
from control.loginC import LoginController
from control.readAccountC import ReadAccountController
from control.searchAccountC import SearchAccountController
from control.createAccountC import CreateAccountController
from control.updateAccountC import UpdateAccountController
from control.suspendAccountC import SuspendAccountController
from control.restrictAccountC import RestrictAccountController
from control.removeRestrictionC import RemoveRestrictionController
from control.removeSuspensionC import RemoveSuspensionController
from entity.account import Account

app = Flask(__name__)
app.secret_key = SECRET_KEY

login_controller = LoginController()
read_account_controller = ReadAccountController()
search_account_controller = SearchAccountController()
create_account_controller = CreateAccountController()
update_account_controller = UpdateAccountController()
suspend_account_controller = SuspendAccountController()
restrict_account_controller = RestrictAccountController()
remove_restriction_controller = RemoveRestrictionController()
remove_suspension_controller = RemoveSuspensionController()


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

def restricted_block_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow admin to bypass restriction
        if session.get("role") != "admin" and session.get("status") == "restricted":
            flash("Your account is restricted. You cannot perform this action.", "danger")
            return redirect(url_for("dashboard_redirect"))
        return f(*args, **kwargs)
    return decorated_function

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

        result = login_controller.login(username_or_email, password)

        if result["success"]:
            account = result["account"]
            session["account_id"] = account.account_id
            session["username"] = account.username
            session["full_name"] = account.full_name
            session["role"] = account.role
            session["status"] = account.status

            flash(result["message"], "success")
            return redirect(url_for("dashboard_redirect"))

        flash(result["message"], "danger")

    return render_template("login.html")

'''
---------- Login Functions ----------
'''

@app.route("/dashboard")
@login_required
def dashboard_redirect():
    role = session.get("role")
    dashboard_route = Account.get_dashboard_route(role)

    if dashboard_route:
        return redirect(url_for(dashboard_route))

    flash("Unknown user role.", "danger")
    return redirect(url_for("login"))

'''
---------- Admin Functions ----------
'''

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    keyword = request.args.get("keyword", "").strip()

    if keyword:
        accounts = search_account_controller.search_accounts(keyword)
    else:
        accounts = read_account_controller.read_accounts()

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
        result = create_account_controller.create_account(request.form)

        flash(result["message"], "success" if result["success"] else "danger")

        if result["success"]:
            return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin_account_form.html",
        form_mode="create",
        account=None,
        selected_role=""
    )


@app.route("/admin/accounts/<int:account_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_account(account_id):
    account = update_account_controller.get_account(account_id)

    if not account:
        flash("Account not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    if account.role == "admin":
        flash("Admin account cannot be edited.", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        result = update_account_controller.update_account(account_id, request.form)

        flash(result["message"], "success" if result["success"] else "danger")

        if result["success"]:
            return redirect(url_for("admin_dashboard"))

        account = update_account_controller.get_account(account_id)

    return render_template(
        "admin_account_form.html",
        form_mode="edit",
        account=account,
        selected_role=account.role
    )

@app.route("/admin/accounts/<int:account_id>/restrict", methods=["POST"])
@login_required
@role_required("admin")
def restrict_account(account_id):
    result = restrict_account_controller.restrict_account(account_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/accounts/<int:account_id>/remove-restriction", methods=["POST"])
@login_required
@role_required("admin")
def remove_restriction(account_id):
    result = remove_restriction_controller.remove_restriction(account_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/accounts/<int:account_id>/suspend", methods=["POST"])
@login_required
@role_required("admin")
def suspend_account(account_id):
    result = suspend_account_controller.suspend_account(account_id)

    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/accounts/<int:account_id>/remove-suspension", methods=["POST"])
@login_required
@role_required("admin")
def remove_suspension(account_id):
    result = remove_suspension_controller.remove_suspension(account_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("admin_dashboard"))

'''
---------- Fundraiser Functions ----------
'''

@app.route("/fundraiser")
@login_required
@role_required("fundraiser")
def fundraiser_dashboard():
    return render_template("fundraiser_dashboard.html", user_name=session.get("full_name"))

'''
---------- Doner Functions ----------
'''

@app.route("/doner")
@login_required
@role_required("doner")
def doner_dashboard():
    return render_template("doner_dashboard.html", user_name=session.get("full_name"))

'''
---------- Manager Functions ----------
'''

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