from entity.account import Account


class ReadAccountController:
    def read_accounts(self):
        return Account.get_all_accounts()