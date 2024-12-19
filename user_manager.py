import json
import os
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
        self.initialize_user_data()

    def initialize_user_data(self):
        if not os.path.exists(self.USER_DATA_FILE):
            with open(self.USER_DATA_FILE, 'w') as file:
                json.dump({}, file)

    def load_user_data(self):
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

    def save_user_data(self, data):
        with open(self.USER_DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def register_user(self):
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
        users = self.load_user_data()

        users[login]["password"] = new_password
        users[login]["birth_date"] = new_birth_date

        self.save_user_data(users)
        print(f"{Fore.GREEN}"
              f"Налаштування успішно оновлено!"
              f"{Style.RESET_ALL}")















