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
from entity.account import Account
from control.removeRestrictionC import RemoveRestrictionController
from control.removeSuspensionC import RemoveSuspensionController
from control.createFraC import CreateFraController
from control.readFraC import ReadFraController
from control.searchFraC import SearchFraController
from control.updateFraC import UpdateFraController
from control.cancelFraC import CancelFraController
from control.reactivateFraC import ReactivateFraController
from control.searchPublicFraC import SearchPublicFraController
from control.readPublicFraC import ReadPublicFraController
from control.addFavouriteC import AddFavouriteController
from control.removeFavouriteC import RemoveFavouriteController
from control.readFavouriteC import ReadFavouriteController
from control.createDonationC import CreateDonationController
from control.readDonationHistoryC import ReadDonationHistoryController
from control.searchDonationHistoryC import SearchDonationHistoryController
from control.readFraStatisticsC import ReadFraStatisticsController
from control.readCompletedFraC import ReadCompletedFraController
from entity.favourite import Favourite
from entity.fra import FRA

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
create_fra_controller = CreateFraController()
read_fra_controller = ReadFraController()
search_fra_controller = SearchFraController()
update_fra_controller = UpdateFraController()
cancel_fra_controller = CancelFraController()
reactivate_fra_controller = ReactivateFraController()
search_public_fra_controller = SearchPublicFraController()
read_public_fra_controller = ReadPublicFraController()
add_favourite_controller = AddFavouriteController()
remove_favourite_controller = RemoveFavouriteController()
read_favourite_controller = ReadFavouriteController()
create_donation_controller = CreateDonationController()
read_donation_history_controller = ReadDonationHistoryController()
search_donation_history_controller = SearchDonationHistoryController()
read_fra_statistics_controller = ReadFraStatisticsController()
read_completed_fra_controller = ReadCompletedFraController()


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
    keyword = request.args.get("keyword", "").strip()
    fundraiser_account_id = session.get("account_id")

    if keyword:
        fra_list = search_fra_controller.search_fra(fundraiser_account_id, keyword)
    else:
        fra_list = read_fra_controller.read_fra(fundraiser_account_id)

    return render_template(
        "fundraiser_dashboard.html",
        user_name=session.get("full_name"),
        fra_list=fra_list,
        keyword=keyword
    )

@app.route("/fundraiser/fra/create", methods=["GET", "POST"])
@login_required
@role_required("fundraiser")
@restricted_block_required
def create_fra():
    if request.method == "POST":
        result = create_fra_controller.create_fra(session.get("account_id"), request.form)

        flash(result["message"], "success" if result["success"] else "danger")

        if result["success"]:
            return redirect(url_for("fundraiser_dashboard"))

    return render_template(
        "fra_form.html",
        form_mode="create",
        fra=None
    )


@app.route("/fundraiser/fra/<int:fra_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("fundraiser")
@restricted_block_required
def edit_fra(fra_id):
    fra = update_fra_controller.get_fra(fra_id)

    if not fra:
        flash("FRA not found.", "danger")
        return redirect(url_for("fundraiser_dashboard"))

    if fra.fundraiser_account_id != session.get("account_id"):
        flash("You can only edit your own FRA.", "danger")
        return redirect(url_for("fundraiser_dashboard"))

    if request.method == "POST":
        result = update_fra_controller.update_fra(
            fra_id,
            session.get("account_id"),
            request.form
        )

        flash(result["message"], "success" if result["success"] else "danger")

        if result["success"]:
            return redirect(url_for("fundraiser_dashboard"))

        fra = update_fra_controller.get_fra(fra_id)

    return render_template(
        "fra_form.html",
        form_mode="edit",
        fra=fra
    )


@app.route("/fundraiser/fra/<int:fra_id>/cancel", methods=["POST"])
@login_required
@role_required("fundraiser")
@restricted_block_required
def cancel_fra(fra_id):
    result = cancel_fra_controller.cancel_fra(
        fra_id,
        session.get("account_id")
    )

    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("fundraiser_dashboard"))


@app.route("/fundraiser/fra/<int:fra_id>/reactivate", methods=["POST"])
@login_required
@role_required("fundraiser")
@restricted_block_required
def reactivate_fra(fra_id):
    result = reactivate_fra_controller.reactivate_fra(
        fra_id,
        session.get("account_id")
    )

    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("fundraiser_dashboard"))

@app.route("/fundraiser/fra/statistics")
@login_required
@role_required("fundraiser")
def fra_statistics():
    stats = read_fra_statistics_controller.read_statistics(session.get("account_id"))

    return render_template(
        "fra_statistics.html",
        stats=stats
    )


@app.route("/fundraiser/fra/completed")
@login_required
@role_required("fundraiser")
def completed_fras():
    completed_stats = read_completed_fra_controller.read_completed_closed_fras(
        session.get("account_id")
    )

    return render_template(
        "completed_fras.html",
        completed_stats=completed_stats
    )
'''
---------- Doner Functions ----------
'''

@app.route("/doner")
@login_required
@role_required("doner")
def doner_dashboard():
    fra_keyword = request.args.get("fra_keyword", "").strip()

    fra_list = search_public_fra_controller.search_fra(fra_keyword)

    return render_template(
        "doner_dashboard.html",
        user_name=session.get("full_name"),
        fra_list=fra_list,
        fra_keyword=fra_keyword
    )

@app.route("/doner/favourites")
@login_required
@role_required("doner")
def doner_favourites():
    favourites = read_favourite_controller.read_favourites(session.get("account_id"))

    return render_template(
        "doner_favourites.html",
        favourites=favourites
    )

@app.route("/doner/donation-history")
@login_required
@role_required("doner")
def doner_donation_history():
    donation_keyword = request.args.get("donation_keyword", "").strip()
    doner_account_id = session.get("account_id")

    if donation_keyword:
        donation_history = search_donation_history_controller.search_history(
            doner_account_id,
            donation_keyword
        )
    else:
        donation_history = read_donation_history_controller.read_history(doner_account_id)

    return render_template(
        "doner_donation_history.html",
        donation_history=donation_history,
        donation_keyword=donation_keyword
    )

@app.route("/doner/fra/<int:fra_id>")
@login_required
@role_required("doner")
def view_fra(fra_id):
    fra = read_public_fra_controller.get_fra(fra_id)

    if not fra:
        flash("FRA not found.", "danger")
        return redirect(url_for("doner_dashboard"))

    FRA.increment_view_count(fra_id)

    fra = read_public_fra_controller.get_fra(fra_id)

    is_favourite = Favourite.is_favourite(session.get("account_id"), fra_id)

    return render_template(
        "fra_view.html",
        fra=fra,
        is_favourite=is_favourite
    )


@app.route("/doner/fra/<int:fra_id>/favourite", methods=["POST"])
@login_required
@role_required("doner")
@restricted_block_required
def add_favourite(fra_id):
    result = add_favourite_controller.add_favourite(session.get("account_id"), fra_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("view_fra", fra_id=fra_id))


@app.route("/doner/fra/<int:fra_id>/remove-favourite", methods=["POST"])
@login_required
@role_required("doner")
@restricted_block_required
def remove_favourite(fra_id):
    result = remove_favourite_controller.remove_favourite(session.get("account_id"), fra_id)
    flash(result["message"], "success" if result["success"] else "danger")
    return redirect(url_for("doner_dashboard"))


@app.route("/doner/fra/<int:fra_id>/donate", methods=["GET", "POST"])
@login_required
@role_required("doner")
@restricted_block_required
def donate_fra(fra_id):
    fra = read_public_fra_controller.get_fra(fra_id)

    if not fra:
        flash("FRA not found.", "danger")
        return redirect(url_for("doner_dashboard"))

    if request.method == "POST":
        amount = request.form.get("amount", "")

        result = create_donation_controller.create_donation(
            session.get("account_id"),
            fra_id,
            amount
        )

        flash(result["message"], "success" if result["success"] else "danger")

        if result["success"]:
            return redirect(url_for("view_fra", fra_id=fra_id))

    return render_template("fake_payment.html", fra=fra)

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