import os
import getpass
from dataclasses import dataclass, asdict, replace
import base64
import pickle
from passlib import pwd
from filehandler import FileHandler
from filehandler import EncryptionHandler
from utilities import Utilities, PasswordHasher


class User:
    def __init__(self, username: str, password: str=None, hashed_password: str=None):
        """
        Initialize a User object with username and (hashed or unhashed) password.

        Raises:
            ValueError: If neither a hashed nor an unhashed password is provided.
        """
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

    def change_password(self, new_password: str):
        self.password = new_password
        self.password = PasswordHasher.hash_password(self.password)

    def to_dict(self):
        """Convert User object to a dictionary"""
        return {
            'username': self.username,
            'password': self.password,
        }


class UserManager:
    def __init__(self, users_filepath='users.json'):
        """Initializes new filehandler (default: users.json) and gets the users from it to instance users"""
        self.user_handler = FileHandler(users_filepath)
        self.users = self.get_users()

    def get_users(self) -> list:
        """From users.json load all the master users credentials"""
        users_data = self.user_handler.read_json()
        if users_data is not None:
            users = []
            for data in users_data:
                users.append(User(data['username'], hashed_password=data['password']))
            return users
        else:
            return []
    
    def save_users(self):
        """Turn user objects to dicts and write to json"""
        users_data = [user.to_dict() for user in self.users]
        self.user_handler.write_json(users_data)

    def add_user(self, new_user: User):
        """If username does not exist, create a new master user"""
        if not any(new_user.username == user.username for user in self.users):
            self.users.append(new_user)
            return True
        return False

    def input_new_user(self):
        """Cli interface for adding a master user"""
        username = input('Username: ')
        password = getpass.getpass('Enter password: ')

        if self.add_user(User(username, password)):
            print('New user created.')
        else:
            print('Username already exists.')

    def login(self):
        """Check if username password are correct if so create an instance of UserAcccountsManager"""
        username = input('Username: ')
        password = getpass.getpass('Password: ')

        for user in self.users:
            if user.username == username and PasswordHasher.check_password(password, user.password):
                # with username create an instance of user data handler for data access and manipulation
                self.user_account_manager = UserAccountsManager(username, password.encode())
                self.current_user = user
                return username
        return None

    def save_user_accounts(self):
        """Save user accounts to json"""
        self.user_account_manager.save_user_accounts()

    def logout(self):
        self.current_user = None
        self.save_user_accounts()       

    def change_master_password(self):
        """Change master password with confirmation"""
        if self.current_user is not None:
            password = getpass.getpass('Enter master password to confirm: ')
            if PasswordHasher.check_password(password, self.current_user.password):
                try:
                    password = getpass.getpass('Enter new master password: ')
                    self.current_user.change_password(password)
                except ValueError as e:
                    print(str(e))
                else:
                    print('Master password changed successfully.')
            else:
                print('Incorrect master password.')

    def remove_user(self):
        """Remove user and user data from the system with confirmation"""
        if self.current_user is not None:
            password = getpass.getpass('Enter master password to confirm: ')
            if PasswordHasher.check_password(password, self.current_user.password):
                username = self.current_user.username
    
                file_path = f'userdata/{username}.json'
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"{username} data has been removed.")
                    self.user_account_manager = None
                else:
                    print(f"{username} data does not exist.")

                self.users.remove(self.current_user)
                print('User removed from system.')

                self.save_users()
                return True
            else:
                print('Incorrect master password.')
        return False


@dataclass
class UserAccount:
    """Represents a user account with platform, username, and password"""
    platform: str
    username: str
    password: str


class UserAccountsManager():
    def __init__(self, username: str, password: bytes):
        """
        Initializes file handler from username
        Gets salt from file or creates new one
        Initializes encryption handler
        Using both handlers gets accounts data
        """
        Utilities.create_directory('userdata')
        self.fh = FileHandler(filepath=f'userdata/{username}.json')
        self.salt = self.get_salt()
        self.eh = EncryptionHandler(password, self.salt)
        self.accounts = self.get_user_data()

    def save_user_accounts(self):
        """Saves accounts encrypted data alongside the encryption salt in a dict to a json file"""
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
        """Gets salt from json, or generate a new one"""
        data = self.fh.read_json()
        if data is not None:
            salt = data.get('salt')
            if salt is not None:
                return bytes.fromhex(salt)
        return EncryptionHandler.generate_salt()      

    def get_user_data(self) -> list:
        """Gets user data from json, decrypts it and converts them back to UserAccount objects"""
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
                if isinstance(decrypted_data, dict):
                    user_account = replace(UserAccount(**decrypted_data))
                    decrypted_accounts.append(user_account)
            except Exception as e:
                print(f"Error loading decrypted data: {e}")

        return decrypted_accounts

    def add_account(self, platform: str, username: str, password: str):
        self.accounts.append(UserAccount(platform, username, password))

    def get_account_credentials(self, platform: str):
        """Gets account username and password clear values of the requested platform"""
        for account in self.accounts:
            if platform == account.platform:
                return account.username, account.password

    def replace_account_password(self, platform: str, password: str):
        """Replaces platform password"""
        for account in self.accounts:
            if platform == account.platform:
                account.password = password
                return True
        return False

    def generate_secure_password(self, length: int=14):
        """Generates strong password of desired length"""
        return pwd.genword(length=length)

    def remove_account(self, platform: str):
        """Account removal proccess with confirmation"""
        for account in self.accounts:
            if platform == account.platform:
                if Utilities.yes_no(f'Are you sure you want to delete {platform} credentials?'):
                    self.accounts.remove(account)
                    return True
        return False