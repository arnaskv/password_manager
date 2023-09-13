import pytest
from utilities import PasswordHasher
from filehandler import FileHandler, EncryptionHandler


def test_password_hasher():
    pw_hash = PasswordHasher.hash_password('123Password')

    assert PasswordHasher.check_password('123pass', pw_hash) == False
    assert PasswordHasher.check_password('123Password', pw_hash) == True


@pytest.fixture
def encryption_handler():
    password = b'112233Aa'
    handler = EncryptionHandler(password)
    yield handler


def test_encrypt_decrypt(encryption_handler):
    data = b'Some secret data to be encrypted'

    encrypted_data = encryption_handler.encrypt(data)
    decrypted_data = encryption_handler.decrypt(encrypted_data)

    assert decrypted_data == data


TEST_FILE_PATH = "test_data.json"

@pytest.fixture
def file_handler():
    return FileHandler(TEST_FILE_PATH)

def test_read_json(file_handler):
    test_data = {"key1": "value1", "key2": "value2"}

    file_handler.write_json(test_data)
    read_data = file_handler.read_json()

    assert read_data == test_data
