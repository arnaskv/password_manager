import os
import bcrypt


class Utilities:
    @staticmethod
    def yes_no(prompt):
        """
        Promts user to choose [Yes/No]
        
        Returns:
            bool value of the answer
        """
        while True:
            answer = input(f'{prompt}\n[Yes/No] ').strip().lower()
            if  answer in ['yes', 'y']:
                return True
            elif answer in ['no', 'n']:
                return False
    
    @staticmethod
    def wait_for_keypress():
        try:
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            pass 


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode()
        return  bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode()

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    