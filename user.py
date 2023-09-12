import bcrypt
import getpass
from dataclasses import dataclass, asdict, replace
import base64
import pickle
from passlib import pwd
from filehandler import FileHandler
from filehandler import EncryptionHandler
from utilities import Utilities


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode()
        return  bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode()

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())


class User:
    def __init__(self, username: str, password: str=None, hashed_password: str=None):
        self.username = username

        if not (password or hashed_password):
            raise ValueError("Either a hashed or unhashed password must be provided.")
        if hashed_password:
            self._password = hashed_password
        elif password:
            self.password = PasswordHasher.hash_password(password)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        # Check for password complexity
        if not (any(c.islower() for c in value) and
                any(c.isupper() for c in value) and
                any(c.isdigit() for c in value)):
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, and one digit.")

        self._password = value

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
        }


class UserManager:
    def __init__(self, users_filepath='users.json'):
        self.user_handler = FileHandler(users_filepath)
        self.users = self.get_users()

    def get_users(self) -> list:
        users_data = self.user_handler.read_json()
        if users_data is not None:
            users = []
            for data in users_data:
                users.append(User(data['username'], hashed_password=data['password']))
            return users
        else:
            return []
    
    def save_users(self):
        users_data = [user.to_dict() for user in self.users]
        self.user_handler.write_json(users_data)

    def add_user(self, new_user: User):
        if not any(new_user.username == user.username for user in self.users):
            self.users.append(new_user)
            return True
        return False

    def input_new_user(self):
        username = input('Username: ')
        password = getpass.getpass('Enter password: ')

        if self.add_user(User(username, password)):
            print('New user created.')
        else:
            print('Username already exists.')

    def login(self):
        username = input('Username: ')
        password = getpass.getpass('Password: ')

        for user in self.users:
            if user.username == username and PasswordHasher.check_password(password, user.password):
                # with username create an instance of user data handler for data access and manipulation
                self.user_account_manager = UserAccountsManager(username, password.encode())
                return username
        return None

    def logout(self):
        self.user_account_manager.save_user_accounts()

    def remove_user(self):
        pass


@dataclass
class UserAccount:
    platform: str
    username: str
    password: str


class UserAccountsManager():
    def __init__(self, username: str, password: bytes):
        self.fh = FileHandler(filepath=f'userdata/{username}')
        self.salt = self.get_salt()
        self.eh = EncryptionHandler(password, self.salt)
        self.accounts = self.get_user_data()

    def save_user_accounts(self):
        if self.accounts is None:
            return

        encrypted_data = []
        for account in self.accounts:
            account_bytes= pickle.dumps(asdict(account))
            encrypted_bytes = self.eh.encrypt(account_bytes)
            # Convert the encrypted bytes to Base64-encoded string
            encrypted_data.append(base64.b64encode(encrypted_bytes).decode('utf-8'))

        data = {
            'accounts': encrypted_data,
            'salt': self.salt.hex(),
        }
        self.fh.write_json(data)

    def get_salt(self) -> str:
        """Gets salt from json or generates a new one"""
        data = self.fh.read_json()
        if data is not None:
            salt = data.get('salt')
            if salt is not None:
                return bytes.fromhex(salt)
        return EncryptionHandler.generate_salt()
            

    def get_user_data(self) -> list:
        data = self.fh.read_json()

        if data is not None:
            encrypted_accounts = data.get('accounts')
        else:
            return []
        
        decrypted_accounts = []
        for account in encrypted_accounts:
            decoded_bytes = base64.b64decode(account)
            decrypted_bytes = self.eh.decrypt(decoded_bytes)


            try:
                decrypted_data = pickle.loads(decrypted_bytes)
                print(decrypted_data)
                if isinstance(decrypted_data, dict):
                    user_account = replace(UserAccount(**decrypted_data))
                    decrypted_accounts.append(user_account)
            except Exception as e:
                print(f"Error loading decrypted data: {e}")

        return decrypted_accounts

    def add_account(self, platform: str, username: str, password: str):
        self.accounts.append(UserAccount(platform, username, password))

    def get_account_credentials(self, platform: str):
        for account in self.accounts:
            if platform == account.platform:
                return account.username, account.password

    def replace_account_password(self, platform: str, password: str):
        for account in self.accounts:
            if platform == account.platform:
                account.password = password
                return True
        return False

    def generate_secure_password(self, length: int=14):
        """Generates strong password of desired length"""
        return pwd.genword(length=length)

    def remove_account(self, platform: str):
        for account in self.accounts:
            if platform == account.platform:
                if Utilities.yes_no(f'Are you sure you want to delete {platform} credentials?'):
                    self.accounts.remove(account)
                    return True
        return False