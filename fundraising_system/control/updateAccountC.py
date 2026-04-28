from entity.account import Account


class UpdateAccountController:
    def get_account(self, account_id):
        return Account.find_by_id(account_id)

    def update_account(self, account_id, form_data):
        return Account.update_account(
            account_id=account_id,
            username=form_data.get("username", ""),
            full_name=form_data.get("full_name", ""),
            email=form_data.get("email", ""),
            role=form_data.get("role", ""),
            new_password=form_data.get("new_password", "")
        )