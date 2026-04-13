import os
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "fundraising.db")

# New session key every startup = auto logout on rerun
SECRET_KEY = secrets.token_hex(32)