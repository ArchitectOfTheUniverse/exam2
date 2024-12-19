from rich.console import Console
from rich.table import Table
from quiz_loader import IQuizLoader
from quiz_category import MixedCategory, SpecificCategory
from quiz_result_manager import IQuizResultManager
from user_manager import IUserManager
from colorama import Fore, Style
from victorine_utility import VictorineUtilityMenu, QuizDataManager


class QuizOrchestrator:
    def __init__(
        self,
        user_manager: IUserManager,
        result_manager: IQuizResultManager,
        quiz_loader: IQuizLoader,
        console: Console = Console(),
        quiz_data_manager: QuizDataManager = QuizDataManager(),

    ):
        self.victorine_utility = VictorineUtilityMenu(quiz_data_manager)
        self.user_manager = user_manager
        self.result_manager = result_manager
        self.quiz_loader = quiz_loader
        self.console = console

    def display_main_menu(self):
        table = Table(title="Головне меню")
        table.add_column()
        table.add_column()
        table.add_row("1", f"Вхід")
        table.add_row("2", "Реєстрація")
        table.add_row("3", "Вихід")
        self.console.print(table)

    def display_user_menu(self, is_admin: bool = False):
        table = Table(title="Меню користувача")
        table.add_column()
        table.add_column()
        table.add_row("1", "Стартувати нову вікторину")
        table.add_row("2", "Переглянути результати своїх минулих вікторин")
        table.add_row("3", "Подивитися топ-20 за конкретною вікториною")
        table.add_row("4", "Змінити налаштування (пароль, дата народження)")
        table.add_row("5", "Вихід")
        if is_admin:
            table.add_row("0", "Редагування")

        self.console.print(table)

    def get_unique_categories(self):
        questions = self.quiz_loader.load_questions()
        categories = set(
            question["category"] for question in questions
        )
        return sorted(categories)

    def display_category_menu(self, categories: list):
        unique_categories = self.get_unique_categories()

        table = Table(title="Вибір категорії")
        table.add_column()
        table.add_column()

        for idx, category in enumerate(unique_categories, 1):
            table.add_row(str(idx), category.capitalize())
        table.add_row(str(len(unique_categories) + 1), "Змішана")
        self.console.print(table)

    def start_quiz(self, login: str, category: str):
        questions = self.quiz_loader.load_questions()

        print(f"{Fore.BLUE}"
              f"\nЗапущена вікторина з категорії {category}"
              f"{Style.RESET_ALL}")

        if category == "Змішана":
            quiz_category = MixedCategory(questions)
        else:
            quiz_category = SpecificCategory(questions, category)

        quiz_category.load_questions()
        questions = quiz_category.get_questions()

        score = 0

        for idx, question in enumerate(questions, 1):
            print(f"\nПитання {idx}: {question['question']}")
            for i, option in enumerate(question["options"], 1):
                print(f"{i}. {option}")

            answer = input(
                f"{Fore.YELLOW}"
                f"Виберіть правильну відповідь (або кілька, через кому): "
                f"{Style.RESET_ALL}"
            )

            correct_answers = set([str(i + 1) for i in
                                   range(len(question["options"])) if
                                   question["options"][i]
                                   in question["correct_answers"]])
            user_answers = set(answer.split(','))

            if user_answers == correct_answers:
                print(f"{Fore.GREEN}Правильна відповідь!{Style.RESET_ALL}")
                score += 1
            else:
                print(f"{Fore.RED}Невірно.{Style.RESET_ALL}")

        print(f"{Fore.BLUE}"
              f"\nВаша оцінка: {score} з {len(questions)}"
              f"{Style.RESET_ALL}")

        self.result_manager.save_quiz_result(login, category, score)

    def display_results(self, login: str):
        print(f"{Fore.BLUE}"
              f"\nПерегляд результатів для користувача {login}:"
              f"{Style.RESET_ALL}")

        quiz_results = self.result_manager.get_user_results(login)

        if not quiz_results:
            print(f"{Fore.BLUE}"
                  f"У вас немає результатів вікторин."
                  f"{Style.RESET_ALL}")
            return

        for category, results in quiz_results.items():
            table = Table(title=f"Результати для категорії {category}")
            table.add_column("Date", justify="center")
            table.add_column("Score", justify="center")

            for result in results:
                table.add_row(result["date"], str(result["score"]))

            self.console.print(table)

    def display_top_20(self, category: str):
        print(f"{Fore.BLUE}"
              f"\nПерегляд топ-20 для категорії {category}:"
              f"{Style.RESET_ALL}")

        top_scores = self.result_manager.get_top_20(category)

        table = Table(title=f"Топ-20 для категорії {category}")
        table.add_column("Place", justify="center")
        table.add_column("User", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Date", justify="center")

        for idx, (user, score, date) in enumerate(top_scores, 1):
            table.add_row(str(idx), user, str(score), date)

        self.console.print(table)

    def main_menu(self):
        while True:
            self.display_main_menu()
            choice = input(f"{Fore.YELLOW}"
                           f"Оберіть опцію (1-3): "
                           f"{Style.RESET_ALL}")

            if choice == "1":
                login = self.user_manager.login_user()
                self.user_menu(login)
            elif choice == "2":
                self.user_manager.register_user()
            elif choice == "3":
                print(f"{Fore.BLUE}"
                      f"До побачення!"
                      f"{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}"
                      f"Невірний вибір. Спробуйте ще раз."
                      f"{Style.RESET_ALL}")

    def user_menu(self, login: str):
        is_admin = login.lower().strip() == "admin"

        while True:
            self.display_user_menu(is_admin=is_admin)
            choice = input(f"{Fore.YELLOW}"
                           f"Оберіть опцію (1-5): "
                           f"{Style.RESET_ALL}")

            if choice == "1":
                unique_categories = self.get_unique_categories()

                self.display_category_menu(unique_categories)

                category_choice = input(f"{Fore.BLUE}"
                                        f"Оберіть категорію: "
                                        f"{Style.RESET_ALL}")

                if category_choice.isdigit():
                    category_choice = int(category_choice)
                    if category_choice <= len(unique_categories):
                        category = unique_categories[category_choice - 1]
                    elif category_choice == len(unique_categories) + 1:
                        category = "Змішана"
                    else:
                        print(f"{Fore.RED}"
                              f"Невірний вибір категорії."
                              f"{Style.RESET_ALL}")
                        return
                else:
                    print(f"{Fore.RED}"
                          f"Невірний вибір категорії."
                          f"{Style.RESET_ALL}")
                    return

                self.start_quiz(login, category)
            elif choice == "2":
                self.display_results(login)
            elif choice == "3":
                print(f"{Fore.BLUE}"
                      f"Перегляд топ-20 за конкретною вікториною:"
                      f"{Style.RESET_ALL}")

                unique_categories = self.get_unique_categories()

                self.display_category_menu(unique_categories)

                category_choice = input(f"{Fore.YELLOW}"
                                        f"Оберіть категорію: "
                                        f"{Style.RESET_ALL}")

                if category_choice.isdigit():
                    category_choice = int(category_choice)
                    if category_choice <= len(unique_categories):
                        category = unique_categories[category_choice - 1]
                    elif category_choice == len(unique_categories) + 1:
                        category = "Змішана"
                    else:
                        print(f"{Fore.RED}"
                              f"Невірний вибір категорії."
                              f"{Style.RESET_ALL}")
                        return
                else:
                    print(f"{Fore.RED}"
                          f"Невірний вибір категорії."
                          f"{Style.RESET_ALL}")
                    return

                self.display_top_20(category)
            elif choice == "4":
                print(f"{Fore.BLUE}"
                      f"\nЗміна налаштувань"
                      f"{Style.RESET_ALL}")
                new_password = input(f"{Fore.YELLOW}"
                                     f"Введіть новий пароль: "
                                     f"{Style.RESET_ALL}")
                new_birth_date = input(
                    f"{Fore.YELLOW}"
                    f"Введіть нову дату народження (РРРР-ММ-ДД): "
                    f"{Style.RESET_ALL}"
                )
                self.user_manager.update_user_settings(
                    login, new_password, new_birth_date
                )
            elif choice == "5":
                print(f"{Fore.BLUE}"
                      f"Вихід із програми. До побачення!"
                      f"{Style.RESET_ALL}")
                break
            elif is_admin and choice == "0":
                self.victorine_utility.run()
            else:
                print(f"{Fore.RED}"
                      f"Невірний вибір. Спробуйте ще раз."
                      f"{Style.RESET_ALL}")