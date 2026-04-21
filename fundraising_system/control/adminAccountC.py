from werkzeug.security import generate_password_hash
from repository.account_repository import AccountRepository
from repository.user_profile_repository import UserProfileRepository


class AdminAccountController:
    def __init__(self):
        self.account_repository = AccountRepository()
        self.user_profile_repository = UserProfileRepository()
        self.allowed_roles = ["fundraiser", "doner", "manager"]
        self.allowed_statuses = ["active", "restricted", "suspended"]

    def is_admin_account(self, account_id):
        role = self.get_role_by_account_id(account_id)
        return role == "admin"

    def get_all_accounts(self):
        accounts = self.account_repository.get_all_accounts()
        results = []

        for account in accounts:
            profile = self.user_profile_repository.find_by_account_id(account.account_id)
            role = profile.role if profile else "No Profile"

            results.append({
                "account_id": account.account_id,
                "username": account.username,
                "full_name": account.full_name,
                "email": account.email,
                "status": account.status,
                "created_at": account.created_at,
                "role": role
            })

        return results

    def search_accounts(self, keyword):
        if not keyword or not keyword.strip():
            return self.get_all_accounts()

        accounts = self.account_repository.search_accounts(keyword.strip())
        results = []

        for account in accounts:
            profile = self.user_profile_repository.find_by_account_id(account.account_id)
            role = profile.role if profile else "No Profile"

            if (
                keyword.lower() in account.username.lower()
                or keyword.lower() in account.full_name.lower()
                or keyword.lower() in account.email.lower()
                or keyword.lower() in role.lower()
            ):
                results.append({
                    "account_id": account.account_id,
                    "username": account.username,
                    "full_name": account.full_name,
                    "email": account.email,
                    "status": account.status,
                    "created_at": account.created_at,
                    "role": role
                })

        return results

    def get_account_by_id(self, account_id):
        return self.account_repository.find_by_id(account_id)

    def get_role_by_account_id(self, account_id):
        profile = self.user_profile_repository.find_by_account_id(account_id)
        return profile.role if profile else ""

    def create_account(self, username, full_name, email, password, role, status="active"):
        username = username.strip()
        full_name = full_name.strip()
        email = email.strip()
        status = "active"

        if not username or not full_name or not email or not password or not role or not status:
            return {"success": False, "message": "All fields are required."}

        if role not in self.allowed_roles:
            return {"success": False, "message": "Invalid role selected."}

        if status not in self.allowed_statuses:
            return {"success": False, "message": "Invalid status selected."}
        
        if role == "admin":
            return {"success": False, "message": "Admin role cannot be assigned."}

        if self.account_repository.username_exists(username):
            return {"success": False, "message": "Username already exists."}

        if self.account_repository.email_exists(email):
            return {"success": False, "message": "Email already exists."}

        password_hash = generate_password_hash(password)

        new_account_id = self.account_repository.create_account(
            username=username,
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            status=status
        )

        self.user_profile_repository.create_profile(new_account_id, role)

        return {"success": True, "message": "Account created successfully."}

    def update_account(self, account_id, username, full_name, email, role, status, new_password=None):
        account = self.account_repository.find_by_id(account_id)
        if not account:
            return {"success": False, "message": "Account not found."}

        current_role = self.get_role_by_account_id(account_id)

        if current_role == "admin":
            return {"success": False, "message": "The admin account cannot be edited."}
        
        username = username.strip()
        full_name = full_name.strip()
        email = email.strip()

        if not username or not full_name or not email or not role or not status:
            return {"success": False, "message": "Please fill in all required fields."}

        if role not in self.allowed_roles:
            return {"success": False, "message": "Invalid role selected."}

        if status not in self.allowed_statuses:
            return {"success": False, "message": "Invalid status selected."}
        
        if role == "admin":
            return {"success": False, "message": "Admin role cannot be assigned."}

        if self.account_repository.username_exists(username, exclude_account_id=account_id):
            return {"success": False, "message": "Username already exists."}

        if self.account_repository.email_exists(email, exclude_account_id=account_id):
            return {"success": False, "message": "Email already exists."}

        self.account_repository.update_account(
            account_id=account_id,
            username=username,
            full_name=full_name,
            email=email,
            status=status
        )

        profile = self.user_profile_repository.find_by_account_id(account_id)
        if profile:
            self.user_profile_repository.update_profile_by_account_id(account_id, role)
        else:
            self.user_profile_repository.create_profile(account_id, role)

        if new_password and new_password.strip():
            password_hash = generate_password_hash(new_password.strip())
            self.account_repository.update_password(account_id, password_hash)

        return {"success": True, "message": "Account updated successfully."}

    def suspend_account(self, account_id):
        account = self.account_repository.find_by_id(account_id)
        if not account:
            return {"success": False, "message": "Account not found."}

        role = self.get_role_by_account_id(account_id)
        if role == "admin":
            return {"success": False, "message": "The admin account cannot be suspended."}

        self.account_repository.suspend_account(account_id)
        return {"success": True, "message": "Account suspended successfully."}