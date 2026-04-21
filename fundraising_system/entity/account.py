class Account:
    def __init__(self, account_id, full_name, username, email, password_hash, status, created_at=None):
        self.account_id = account_id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.status = status
        self.created_at = created_at

    def is_suspended(self):
        return self.status == "suspended"

    def is_restricted(self):
        return self.status == "restricted"

    def can_login(self):
        return self.status in ["active", "restricted"]