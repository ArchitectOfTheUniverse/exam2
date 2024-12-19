import json
import os
from datetime import datetime
from typing import Dict, Optional
from abc import ABC, abstractmethod
from colorama import Fore, Style


class IUserManager(ABC):
    @abstractmethod
    def register_user(self) -> Optional[str]:
        pass

    @abstractmethod
    def login_user(self) -> Optional[str]:
        pass

    @abstractmethod
    def update_user_settings(
            self, login: str, new_password: str, new_birth_date: str
    ):
        pass

    @abstractmethod
    def load_user_data(self) -> Dict:
        pass

    @abstractmethod
    def save_user_data(self, data: Dict):
        pass


class UserManager(IUserManager):
    USER_DATA_FILE = "users.json"

    def __init__(self):
        """
        Initializes the UserManager instance by calling the initialize_user_data method, which
        checks if the user data file exists and if not, creates it. If the file is corrupted, it
        is rewritten.
        """
        self.initialize_user_data()

    def initialize_user_data(self):
        """
        Checks if the user data file exists and if not, creates it. If the file is corrupted, it
        is rewritten.

        This method is called in the constructor of the UserManager class and is used to
        initialize the user data file on the first run of the application.

        :return: None
        """
        if not os.path.exists(self.USER_DATA_FILE):
            with open(self.USER_DATA_FILE, 'w') as file:
                json.dump({}, file)

    def load_user_data(self):
        """
        Loads user data from the file specified in USER_DATA_FILE.

        If the file is corrupted, it is rewritten and an empty dictionary is returned.

        :return: A dictionary with user data
        """
        try:
            with open(self.USER_DATA_FILE, 'r') as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    raise ValueError(
                        f"{Fore.RED}"
                        f"Файл користувачів пошкоджений."
                        f"{Style.RESET_ALL}"
                    )
                return data
        except (json.JSONDecodeError, ValueError):
            print(
                f"{Fore.RED}"
                f"Файл користувачів пошкоджений. Перезаписуємо файл."
                f"{Style.RESET_ALL}"
            )
            self.save_user_data({})
            return {}
        except Exception as e:
            print(
                f"{Fore.RED}"
                f"Сталася непердбачувана помилка: "
                f"{str(e)}."
                f"{Style.RESET_ALL}"
            )
            return {}

    def save_user_data(self, data):
        """
        Saves user data to the file specified in USER_DATA_FILE.

        This method is used to save user data to the file. If the file is corrupted, it is rewritten.

        :param data: A dictionary with user data
        :return: None
        """
        with open(self.USER_DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def register_user(self):
        """
        Registers a new user.

        This method is used to register a new user. It prompts the user to enter a login and a password.
        If the login already exists, it prompts the user to enter a different login.
        After the user has entered a valid login and password, it creates a new user in the database and
        saves the data to the file specified in USER_DATA_FILE.

        :return: The login of the newly registered user or None if the registration fails
        """
        users = self.load_user_data()

        print("\nРеєстрація")
        login = input(f"{Fore.YELLOW}Введіть логін:{Style.RESET_ALL}")
        if login in users:
            print(
                f"{Fore.LIGHTRED_EX}Логін вже існує. Спробуйте інший."
                f"{Style.RESET_ALL}"
            )

            return None

        password = input(
            f"{Fore.YELLOW}"
            f"Введіть пароль: "
            f"{Style.RESET_ALL}"
        )
        birth_date = input(
            f"{Fore.YELLOW}"
            f"Введіть дату народження (у форматі РРРР-ММ-ДД): "
            f"{Style.RESET_ALL}"
        )

        users[login] = {
            "password": password,
            "birth_date": birth_date,
            "quiz_results": {}
        }

        self.save_user_data(users)
        print(f"{Fore.GREEN}"
              f"Реєстрація успішна!"
              f"{Style.RESET_ALL}")
        return login

    def login_user(self):
        """
        Logs in a user.

        This method is used to log in a user. It prompts the user to enter a login and a password.
        If the login does not exist, it prompts the user to register first.
        If the login exists, it checks the password. If the password is correct, it logs in the user
        and returns the login. If the password is incorrect, it prints an error message and returns None.

        :return: The login of the user or None if the login fails
        """
        users = self.load_user_data()

        print(
            f"{Fore.BLUE}"
            f"\nВхід"
            f"{Style.RESET_ALL}"
        )
        login = input(
            f"{Fore.YELLOW}"
            f"Введіть логін: "
            f"{Style.RESET_ALL}"
        )

        if login not in users:
            print(
                f"{Fore.LIGHTRED_EX}"
                f"Користувач не знайдений. Спершу зареєструйтесь."
                f"{Style.RESET_ALL}"
            )
            return None

        password = input(
            f"{Fore.YELLOW}"
            f"Введіть пароль: "
            f"{Style.RESET_ALL}"
        )

        if users[login]["password"] == password:
            print(f"{Fore.BLUE}"
                  f"Ласкаво просимо, {login}!"
                  f"{Style.RESET_ALL}")
            return login
        else:
            print(f"{Fore.RED}Невірний пароль.{Style.RESET_ALL}")
            return None

    def update_user_settings(self, login, new_password, new_birth_date):
        """
        Updates the user's settings for a given login.

        This method updates the password and birth date for the user
        identified by the provided login. If the login is not found,
        an error message is displayed.

        Args:
            login (str): The login identifier of the user.
            new_password (str): The new password for the user.
            new_birth_date (str): The new birth date for the user in YYYY-MM-DD format.

        Returns:
            None
        """
        users = self.load_user_data()

        if login not in users:
            print(f"{Fore.RED}"
                  f"Користувача з таким логіном не існує."
                  f"{Style.RESET_ALL}")
            return

        users[login]["password"] = new_password
        users[login]["birth_date"] = new_birth_date

        self.save_user_data(users)
        print(f"{Fore.GREEN}"
              f"Налаштування успішно оновлено!"
              f"{Style.RESET_ALL}")















