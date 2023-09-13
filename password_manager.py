import sys
import os
import getpass
from user import UserManager
from utilities import Utilities


def main():
    print("Welcome to your password manager.")
    
    manager = UserManager()
    login_menu(manager)


def login_menu(manager: UserManager):
    """Pops up main menu choices"""
    while True:
        print('\n:::Main menu:::')
        answer = input('\n| (S)ign in | (C)reate an account | (E)xit |  ').strip().lower()
        
        if answer == 's':
            if sign_in(manager):
                user_account_modes(manager)

        elif answer == 'c':
            create_user(manager)
            manager.save_users()

        elif answer == 'e':
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

    
def master_account_options_menu(manager: UserManager):
    """Pops out a menu for master user options"""
    while True:
        print('\n:::Master account options:::')
        answer = input('\n| (C)hange master password | (D)elete master account | (E)xit |  ').strip().lower()
        
        if answer == 'c':
            print('Changing master password.')
            manager.change_master_password()
            manager.save_users

        elif answer == 'd':
            print('Removing user.')
            if manager.remove_user():
                return True

        elif answer == 'e':
            break


def user_account_modes(manager: UserManager):
    """Pops out user account menu choices"""
    while True:
        print('\n:::User accounts options:::')
        print('\n| (A)dd account | (R)emove account | (G)et account credentials |\n| (C)hange password | (S)how all | (M)aster account options |\n| (L)ogout |')
        mode = input().lower().strip()
        # Add account
        if  mode == 'a':
            print('Enter new account credentials.')
            platform = input('Platform: ').strip().lower()
            username = input('Username: ')
            password = getpass.getpass('Password: ')
            manager.user_account_manager.add_account(platform, username, password)
            manager.save_user_accounts()

        # Change account password
        elif mode == 'c':
            print('To change account password enter.')
            platform = input('Platform: ').strip().lower()
            password = getpass.getpass('Password: ')
            if manager.user_account_manager.replace_account_password(platform, password):
                print('Password changed successfully.')
                manager.save_user_accounts()
            else:
                print('Password change failed.')

        # Remove account
        elif mode == 'r':
            print('To remove account credentials enter.')
            platform = input('Platform: ').strip().lower()
            if manager.user_account_manager.remove_account(platform):
                print(f'{platform.capitalize()} credentials removed successfully.')
                manager.save_user_accounts()
            else:
                print(f'{platform.capitalize()} credentials do not exist.')

        # Get account credentials
        elif mode == 'g':
            print('To get credentials enter.')
            platform = input('Platform: ').strip().lower()
            credentials = manager.user_account_manager.get_account_credentials(platform)
            if credentials is None:
                print(f'{platform.capitalize()} credentials do not exist.')
            else:
                print(f'Username: {credentials[0]}\nPassword: {credentials[1]}')
            Utilities.wait_for_keypress()
            # Clears the previous 3 lines
            print("\x1b[3A\x1b[K\x1b[K\x1b[K")

        # Show all available accounts 
        elif mode == 's':
            print('Available accounts:')
            for account in manager.user_account_manager.accounts:
                print(account.platform.capitalize())
            Utilities.wait_for_keypress()

        # Master account options menu
        elif mode == 'm':
            if master_account_options_menu(manager):
                break

        # Logout
        elif mode == 'l':
            manager.logout()
            break
    

if __name__ == '__main__':
    main()