from entity.account import Account


class RemoveRestrictionController:
    def remove_restriction(self, account_id):
        return Account.remove_restriction(account_id)