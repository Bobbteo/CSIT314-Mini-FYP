from entity.account import Account


class RestrictAccountController:
    def restrict_account(self, account_id):
        return Account.restrict_account(account_id)