import json
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class FileHandler:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def read_json(self, mode='r'):
        try:
            with open(self.filepath, mode) as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f'Error decoding JSON in "{self.filepath}"')
            return None

    def write_json(self, data, mode='w'):
        try:
            with open(self.filepath, mode) as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f'Error writing to "{self.filepath}" : {str(e)}')


class EncryptionHandler:
    def __init__(self, password: bytes, salt=None):
        if salt is None:
            self.salt = self.generate_salt()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            iterations=480000,
            salt=salt,
            length=32
        )
        
        # Derive the key from the provided password using PBKDF2
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.f = Fernet(key)

    @staticmethod
    def generate_salt():
        return os.urandom(16) 

    def encrypt(self, data: bytes) -> bytes:
        encrypted_data = self.f.encrypt(data)
        return encrypted_data

    def decrypt(self, encrypted_data: bytes) -> bytes:
        decrypted_data = self.f.decrypt(encrypted_data)
        return decrypted_data