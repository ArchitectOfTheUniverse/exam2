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
        """
        Initializes a QuizOrchestrator instance.

        Args:
            user_manager: An object implementing IUserManager, to manage users.
            result_manager: An object implementing IQuizResultManager, to handle quiz results.
            quiz_loader: An object implementing IQuizLoader, to load questions.
            console: A Console object to print tables. Defaults to Console().
            quiz_data_manager: A QuizDataManager object to manage quiz data. Defaults to QuizDataManager().
        """
        self.victorine_utility = VictorineUtilityMenu(quiz_data_manager)
        self.user_manager = user_manager
        self.result_manager = result_manager
        self.quiz_loader = quiz_loader
        self.console = console

    def display_main_menu(self):
        """
        Displays the main menu.

        The main menu is displayed when the user launches the application.
        It allows the user to choose between logging in, registering, or exiting the application.

        The menu is displayed as a table with two columns: the left column contains the option number,
        and the right column contains a description of the option. The user can then enter the number
        of the desired option to select it.

        :return: None
        """
        table = Table(title="Головне меню")
        table.add_column()
        table.add_column()
        table.add_row("1", f"Вхід")
        table.add_row("2", "Реєстрація")
        table.add_row("3", "Вихід")
        self.console.print(table)

    def display_user_menu(self, is_admin: bool = False):
        """
        Displays the user menu.

        The user menu is displayed after the user logs in.
        It allows the user to choose between:
        - Starting a new quiz
        - Viewing their own quiz results
        - Viewing the top-20 scores for a specific quiz
        - Editing their settings (password, date of birth)
        - Exiting the application

        If the user is an administrator, the menu also allows the user to
        edit the quiz data.

        The menu is displayed as a table with two columns: the left column contains the option number,
        and the right column contains a description of the option. The user can then enter the number
        of the desired option to select it.

        :param is_admin: Whether the user is an administrator. Defaults to False.
        :return: None
        """
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
        """Returns a sorted list of unique categories from the questions dataset."""
        try:
            questions = self.quiz_loader.load_questions()
            if not questions:
                raise ValueError(
                    f"{Fore.RED}"
                    f"Немає доступних питань!"
                    f"{Style.RESET_ALL}"
                )
            categories = set(
                question["category"] for question in questions
            )
            return sorted(categories)
        except Exception as e:
            print(f"{Fore.RED}"
                  f"Помилка при завантаженні категорій: {str(e)}"
                  f"{Style.RESET_ALL}")
            return []

    def display_category_menu(self, categories: list):
        """
        Displays the category menu.

        The category menu is displayed after the user starts a new quiz.
        It allows the user to choose between:
        - A specific category
        - A mixed category (all questions)

        The menu is displayed as a table with two columns: the left column contains the option number,
        and the right column contains a description of the option. The user can then enter the number
        of the desired option to select it.

        :param categories: The list of categories to display in the menu.
        :return: None
        """
        unique_categories = self.get_unique_categories()

        table = Table(title="Вибір категорії")
        table.add_column()
        table.add_column()

        for idx, category in enumerate(unique_categories, 1):
            table.add_row(str(idx), category.capitalize())
        table.add_row(str(len(unique_categories) + 1), "Змішана")
        self.console.print(table)

    def start_quiz(self, login: str, category: str):
        """
        Starts a new quiz.

        This method starts a new quiz for a specific user with a specific category.

        The method first loads the questions for the specified category.
        If the category is "Змішана", the method loads all available questions.
        Otherwise, it loads only the questions for the specified category.

        Then, the method prints a message to the user to inform them that the quiz has started.
        It then iterates over the questions and prints each question to the user.
        The user is then prompted to enter their answer(s) for the question.
        If the user's answer(s) match the correct answer(s), the user is awarded a point.
        The method then prints the user's score at the end of the quiz.
        Finally, the method saves the quiz result to the database.

        :param login: The user's login.
        :param category: The category of the quiz.
        :return: None
        """
        try:
            questions = self.quiz_loader.load_questions()
            if not questions:
                raise ValueError(
                    f"{Fore.RED}"
                    f"Немає доступних питань для цієї категорії."
                    f"{Style.RESET_ALL}"
                )

            print(f"{Fore.BLUE}"
                  f"\nЗапущена вікторина з категорії {category}"
                  f"{Style.RESET_ALL}")

            if category == "Змішана":
                quiz_category = MixedCategory(questions)
            else:
                quiz_category = SpecificCategory(questions, category)

            quiz_category.load_questions()
            questions = quiz_category.get_questions()
            if not questions:
                raise ValueError(
                    f"{Fore.RED}"
                    f"Вибрана категорія не має питань"
                    f"{Style.RESET_ALL}"
                )

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
                    print(f"{Fore.GREEN}"
                          f"Правильна відповідь!"
                          f"{Style.RESET_ALL}")
                    score += 1
                else:
                    print(f"{Fore.RED}Невірно.{Style.RESET_ALL}")

            print(f"{Fore.BLUE}"
                  f"\nВаша оцінка: {score} з {len(questions)}"
                  f"{Style.RESET_ALL}")

            self.result_manager.save_quiz_result(login, category, score)
        except Exception as e:
            print(f"{Fore.RED}"
                  f"Помилка під час запуску вікторини: {str(e)}"
                  f"{Style.RESET_ALL}")

    def display_results(self, login: str):
        """
        Display quiz results for a specific user.

        This method retrieves and displays the quiz results for the user
        identified by the given login. It organizes the results by category
        and presents them in a formatted table. If the user has no quiz results,
        a message indicating the absence of results is printed.

        Args:
            login (str): The login identifier of the user whose results are to be displayed.
        """
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
        """
        Display the top 20 quiz results for a specific category.

        This method retrieves and displays the top 20 quiz results
        for the given category. It fetches the results from the
        result manager, sorts them by score, and presents them in a
        formatted table. If there are fewer than 20 results, all
        available results are displayed.

        Args:
            category (str): The category for which to display the top
                            quiz results.
        """
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
        """
        Display the main menu and handle user choices.

        This method continuously displays the main menu to the user,
        allowing them to choose between logging in, registering, or
        exiting the application. Based on the user's input, it directs
        them to the appropriate action. The loop continues until the
        user chooses to exit.

        User Options:
            1. Log in and navigate to the user menu.
            2. Register a new user account.
            3. Exit the application.
        """
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
        """
        Displays the user menu and handles option selection.

        This method provides the user with the following functionalities:
        1. Taking a quiz in a selected category.
        2. Viewing the user's results.
        3. Viewing the top-20 results in a specific category.
        4. Updating personal settings (password and birth date).
        5. Exiting the program.

        If the user is an administrator (login "admin"), an additional option is available:
        0. Access the quiz utility for managing quizzes.

        Args:
            login (str): The login name of the user to determine access level.

        Returns:
            None
        """
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