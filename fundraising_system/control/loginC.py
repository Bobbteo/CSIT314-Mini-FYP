from werkzeug.security import check_password_hash
from repository.account_repository import AccountRepository

class LoginController:
    def __init__(self):
        self.account_repository = AccountRepository()

    def authenticate(self, username_or_email, password):
        if not username_or_email or not password:
            return {
                "success": False,
                "message": "Please enter both username/email and password."
            }

        account = self.account_repository.find_by_username_or_email(username_or_email)

        if account is None:
            return {
                "success": False,
                "message": "Invalid username/email or password."
            }

        if not account.is_active():
            return {
                "success": False,
                "message": "Your account is not active. Please contact support."
            }

        if not check_password_hash(account.password_hash, password):
            return {
                "success": False,
                "message": "Invalid username/email or password."
            }

        return {
            "success": True,
            "message": f"Welcome, {account.full_name}!",
            "account": account
        }

    def get_dashboard_route(self, role):
        if role == "admin":
            return "admin_dashboard"
        elif role == "fundraiser":
            return "fundraiser_dashboard"
        elif role == "doner":
            return "doner_dashboard"
        elif role == "manager":
            return "manager_dashboard"
        return None