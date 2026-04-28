from entity.account import Account


class CreateAccountController:
    def create_account(self, form_data):
        return Account.create_account(
            username=form_data.get("username", ""),
            full_name=form_data.get("full_name", ""),
            email=form_data.get("email", ""),
            password=form_data.get("password", ""),
            role=form_data.get("role", "")
        )