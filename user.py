from filehandler import FileHandler
import bcrypt


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = self.hash_password(password)

    def hash_password(self):
        bytes = self.password.encode()
        salt = bcrypt.gensalt()
        return  bcrypt.hashpw(bytes, salt)

    def check_password(self, password):
        bytes = password.encode()
        return bcrypt.checkpw(bytes, self.password)


class UserManager:
    def __init__(self):
        self.users = []

    def add_user(self, new_user):
        if new_user.username not in self.users:
            self.users.append(new_user)
            return True
        return False

    def user_exists(self, user):
        if user.username in self.users:
            return True
        return False    
    
    def login(self, username, password):
        for user in self.users:
            if username in user.username:
                return user.check_password(password)
        return False

