from entity.account import Account


class SearchAccountController:
    def search_accounts(self, keyword):
        return Account.search_accounts(keyword)