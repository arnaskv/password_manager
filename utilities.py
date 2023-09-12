import os


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

    @staticmethod
    def file_path(filename, folder_name='userdata'):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return os.path.join(folder_name, f'{filename}.json')