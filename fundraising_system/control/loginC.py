from werkzeug.security import check_password_hash
from repository.account_repository import AccountRepository
from repository.user_profile_repository import UserProfileRepository


class LoginController:
    def __init__(self):
        self.account_repository = AccountRepository()
        self.user_profile_repository = UserProfileRepository()

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

        if account.is_suspended():
            return {
                "success": False,
                "message": "Your account has been suspended. Please contact support."
    }

        if not check_password_hash(account.password_hash, password):
            return {
                "success": False,
                "message": "Invalid username/email or password."
            }

        profile = self.user_profile_repository.find_by_account_id(account.account_id)

        if not profile:
            return {
                "success": False,
                "message": "No user profile assigned to this account."
            }

        return {
            "success": True,
            "message": f"Welcome, {account.full_name}!",
            "account": account,
            "role": profile.role
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