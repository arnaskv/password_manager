import sys
import getpass
import pyperclip
from user import UserManager
from utilities import Utilities


def main():
    print("Welcome to your password manager.\n")
    
    manager = UserManager()
    login_menu(manager)


def login_menu(manager: UserManager):
    while True:
        answer = input('(S)ign in / (C)reate an account / (Q)uit?  ').strip().lower()
        
        if answer == 's':
            if sign_in(manager):
                user_account_modes(manager)
        elif answer == 'c':
            create_user(manager)
        elif answer == 'q':
            manager.save_users()
            sys.exit('Exiting...')

def sign_in(manager: UserManager):
        print('\nTo sign in enter.')
        if username := manager.login():
            print(f'Welcome back {username}!\n')
            return True
        else:
            print('Wrong username/password.\n')

def create_user(manager: UserManager):
    print('\nTo create a new user account enter.')
    try:
        manager.input_new_user()
    except ValueError as e:
        print(f'{str(e)}.\n')

def user_account_modes(manager: UserManager):
    while True:
        mode = input('(A)dd account / (R)emove account / (G)et account credentials /\n (C)hange password / (D)elete master account / (L)ogout?  ').lower().strip()
        if  mode == 'a':
            print('Enter new account credentials.')
            platform = input('Platform: ')
            username = input('Username: ')
            password = getpass.getpass('Password: ')
            manager.user_account_manager.add_account(platform, username, password)

        elif mode == 'c':
            pass

        elif mode == 'r':
            print('To remove account credentials enter.')
            platform = input('Platform: ')
            if manager.user_account_manager.remove_account(platform):
                print(f'{platform.istitle()} credentials removed successfully.')
            else:
                print(f'{platform.istitle()} credentials do not exist.')

        elif mode == 'g':
            print('To get credentials enter.')
            platform = input('Platform: ')
            username, password = manager.user_account_manager.get_account_credentials(platform)
            if username:
                print(f'Username: {username}\nPassword: {password}')
            else:
                print(f'{platform.istitle()} credentials do not exist.')
            Utilities.wait_for_keypress()

        elif mode == 'l':
            manager.logout()
            break
    

if __name__ == '__main__':
    main()