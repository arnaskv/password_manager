from dataclasses import dataclass
from FileHandler import FileHandler
import bcrypt


@dataclass
class User:
    username: str
    password: str

    def hash_password(self):
        bytes = self.password.encode()
        salt = bcrypt.gensalt()
        return  bcrypt.hashpw(bytes, salt)



class UserManager:
    def __init__(self):
        self.users = []

    def add_user(self, username, password):
        new_user = User(username, password)
        self.users.append(new_user)

    def check_user(self, username, password):
        for user in self.users:
            if username = user.username:
                if 

