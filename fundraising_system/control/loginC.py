from entity.account import Account


class LoginController:
    def login(self, username_or_email, password):
        return Account.authenticate(username_or_email, password)