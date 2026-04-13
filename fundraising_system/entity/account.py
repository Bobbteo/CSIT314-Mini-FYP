class Account:
    def __init__(self, account_id, full_name, username, email, password_hash, role, status, created_at=None):
        self.account_id = account_id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.status = status
        self.created_at = created_at

    def is_active(self):
        return self.status == "active"