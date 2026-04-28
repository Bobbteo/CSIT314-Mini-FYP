from entity.account import Account


class SuspendAccountController:
    def suspend_account(self, account_id):
        return Account.suspend_account(account_id)