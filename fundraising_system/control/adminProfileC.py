from repository.user_profile_repository import UserProfileRepository
from repository.account_repository import AccountRepository


class AdminProfileController:
    def __init__(self):
        self.user_profile_repository = UserProfileRepository()
        self.account_repository = AccountRepository()
        self.allowed_roles = ["fundraiser", "doner", "manager"]

    def get_all_profiles(self):
        return self.user_profile_repository.get_all_profiles()

    def search_profiles(self, keyword):
        if not keyword or not keyword.strip():
            return self.user_profile_repository.get_all_profiles()
        return self.user_profile_repository.search_profiles(keyword.strip())

    def get_profile_by_id(self, profile_id):
        return self.user_profile_repository.find_by_id(profile_id)

    def get_accounts_without_profiles(self):
        accounts = self.account_repository.get_accounts_without_profiles()
        non_admin_accounts = []
        for account in accounts:
            if account.username != "admin1":
                non_admin_accounts.append(account)
        return non_admin_accounts

    def create_profile(self, account_id, role):
        if not account_id or not role:
            return {"success": False, "message": "All fields are required."}

        if role not in self.allowed_roles:
            return {"success": False, "message": "Invalid role selected."}

        account = self.account_repository.find_by_id(account_id)
        if not account:
            return {"success": False, "message": "Account not found."}

        if account.username == "admin1":
            return {"success": False, "message": "Admin profile cannot be created here."}

        existing_profile = self.user_profile_repository.find_by_account_id(account_id)
        if existing_profile:
            return {"success": False, "message": "This account already has a profile."}

        self.user_profile_repository.create_profile(account_id, role)
        return {"success": True, "message": "User profile created successfully."}

    def update_profile(self, profile_id, role):
        profile = self.user_profile_repository.find_by_id(profile_id)
        if not profile:
            return {"success": False, "message": "Profile not found."}

        if role not in self.allowed_roles:
            return {"success": False, "message": "Invalid role selected."}

        self.user_profile_repository.update_profile(profile_id, role)
        return {"success": True, "message": "User profile updated successfully."}

    def delete_profile(self, profile_id):
        profile = self.user_profile_repository.find_by_id(profile_id)
        if not profile:
            return {"success": False, "message": "Profile not found."}

        self.user_profile_repository.delete_profile(profile_id)
        return {"success": True, "message": "User profile deleted successfully."}