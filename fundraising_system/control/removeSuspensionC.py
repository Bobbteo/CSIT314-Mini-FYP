from entity.account import Account


class RemoveSuspensionController:
    def remove_suspension(self, account_id):
        return Account.remove_suspension(account_id)