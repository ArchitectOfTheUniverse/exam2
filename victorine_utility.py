import json
from rich.console import Console
from rich.table import Table
from abc import ABC, abstractmethod


class IQuizDataManager(ABC):
    @abstractmethod
    def get_questions(self):
        pass

    @abstractmethod
    def save_questions(self, questions):
        pass


class QuizDataManager(IQuizDataManager):
    def __init__(self, file_path='questions.json'):
        """
        Initializes a QuizDataManager instance.

        Args:
            file_path (str): The path to the JSON file where questions
            are stored. Defaults to 'questions.json'.
        """
        self.file_path = file_path

    def get_questions(self):
        """
        Reads the questions from the JSON file specified by `file_path`.

        Returns:
            list: A list of questions from the JSON file. If the file
            is not found or if there is a JSON decode error, an empty
            list is returned.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If there is an error in decoding the
            JSON file.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("questions", [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Помилка при читанні файлу.")
            return []

    def save_questions(self, questions):
        """
        Writes the questions to the JSON file specified by `file_path`.

        Args:
            questions (list): A list of questions to be written to the file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If there is an error in encoding the JSON file.
        """
        data = {"questions": questions}
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except FileNotFoundError:
            print("Помилка при збереженні файлу.")
        except json.JSONDecodeError:
            print("Помилка при запису файлу.")


class IVictorineUtility(ABC):
    @abstractmethod
    def display_menu(self):
        pass

    @abstractmethod
    def run(self):
        pass


class VictorineUtilityMenu(IVictorineUtility):
    def __init__(
            self, quiz_data_manager: IQuizDataManager,
            console: Console = Console()
    ):
        """
        Initializes a VictorineUtilityMenu instance.

        Args:
            quiz_data_manager (IQuizDataManager): An object to manage quiz data.
            console (Console, optional): A Console object for displaying output. Defaults to a new Console instance.
        """

        self.console = console
        self.quiz_data_manager = quiz_data_manager
        self.menu = {
            "1": "Додати вікторину",
            "2": "Видалити вікторину",
            "3": "Змінити вікторину",
            "4": "Переглянути вікторини",
            "5": "Вихід",
        }

    def display_menu(self):
        """
        Displays the quiz menu.

        This method presents the quiz menu options to the user in a
        formatted table. Each menu option is displayed with an option
        number and a description. The user can then enter the number
        corresponding to their desired action.

        :return: None
        """
        table = Table(title="Меню вікторин")
        table.add_column()
        table.add_column()

        for key, value in self.menu.items():
            table.add_row(key, value)

        self.console.print(table)

    def get_unique_categories(self):
        """
        Retrieves a sorted list of unique categories from the questions dataset.

        This method queries the QuizDataManager for all questions and extracts
        the category from each question. The categories are stored in a set and
        then converted to a sorted list before being returned.

        :return: A sorted list of strings, each representing a unique category.
        """
        questions = self.quiz_data_manager.get_questions()
        categories = set()

        for question in questions:
            if "category" in question:
                categories.add(question["category"])

        return sorted(categories)

    def get_questions_by_category(self, category):
        """
        Retrieves a list of questions for a specified category.

        This method filters the questions dataset to include only those
        questions that belong to the given category.

        Args:
            category (str): The category for which to retrieve questions.

        Returns:
            list: A list of questions that belong to the specified category.
        """
        questions = self.quiz_data_manager.get_questions()
        return [q for q in questions if q["category"] == category]

    def delete_quiz(self):
        """
        Deletes all questions from a specified category.

        This method displays a menu of all available categories and allows the user
        to select a category to delete. Once a category is selected, all questions
        belonging to that category are removed from the dataset.

        :return: None
        """
        categories = self.get_unique_categories()
        if not categories:
            print("Немає доступних категорій для видалення.")
            return

        table = Table(title="Оберіть категорію для видалення")
        table.add_column("№", justify="center")
        table.add_column("Категорія", justify="center")

        for idx, category in enumerate(categories, 1):
            table.add_row(str(idx), category)

        self.console.print(table)

        category_choice = input(
            f"Оберіть категорію для видалення (1-{len(categories)}): "
        )
        try:
            category_choice = int(category_choice)
            if 1 <= category_choice <= len(categories):
                selected_category = categories[category_choice - 1]
                self.remove_category_questions(selected_category)
            else:
                print("Невірний вибір категорії.")
        except ValueError:
            print("Невірний вибір.")

    def remove_category_questions(self, category):
        """
        Removes all questions from the specified category.

        This method filters out questions that belong to the given category
        from the dataset and saves the remaining questions. It then prints a
        confirmation message indicating that all questions from the specified
        category have been deleted.

        Args:
            category (str): The category from which questions should be removed.
        """
        questions = self.quiz_data_manager.get_questions()
        filtered_questions = [
            q for q in questions if q["category"] != category
        ]

        self.quiz_data_manager.save_questions(filtered_questions)
        print(f"Усі запитання з категорії '{category}' були видалені.")

    def add_quiz(self):
        """
        Adds a new question to the specified category.

        This method first prompts the user to enter the category to which
        the new question should be added. It then enters a loop where it
        repeatedly prompts the user to enter the following information until
        the user chooses to stop:

        1. The text of the question
        2. A comma-separated list of options
        3. A comma-separated list of correct answers

        For each question, the entered information is stored in a dictionary
        and added to the list of all questions. The updated list of questions
        is then saved to the dataset.

        :return: None
        """
        category = input("Введіть категорію для вікторини: ")
        questions = self.quiz_data_manager.get_questions()

        while True:
            question_text = input("Введіть запитання: ")
            options = input(
                "Введіть варіанти відповідей (через кому): ").split(','
            )
            correct_answers = input(
                "Введіть правильні відповіді (через кому): ").split(','
            )

            new_question = {
                "category": category,
                "question": question_text,
                "options": options,
                "correct_answers": correct_answers,
            }

            questions.append(new_question)
            self.quiz_data_manager.save_questions(questions)

            print("Запитання додано.")
            continue_choice = input("Додати ще одне питання? (y/n): ")
            if continue_choice.lower() != "y":
                break

    def edit_quiz(self):
        """
        Edits questions within a specified category.

        This method displays a menu of all available categories and allows the user
        to select a category for editing. Once a category is selected, the questions
        within that category are displayed, and the user can choose a question to edit.

        :return: None
        """

        categories = self.get_unique_categories()
        if not categories:
            print("Немає доступних категорій для редагування.")
            return

        table = Table(title="Оберіть категорію для редагування")
        table.add_column("№", justify="center")
        table.add_column("Категорія", justify="center")

        for idx, category in enumerate(categories, 1):
            table.add_row(str(idx), category)

        self.console.print(table)

        category_choice = input(
            f"Оберіть категорію для редагування (1-{len(categories)}): "
        )
        try:
            category_choice = int(category_choice)
            if 1 <= category_choice <= len(categories):
                selected_category = categories[category_choice - 1]
                questions_in_category = (
                    self.get_questions_by_category(selected_category))
                self.display_questions_for_editing(questions_in_category)
            else:
                print("Невірний вибір категорії.")
        except ValueError:
            print("Невірний вибір.")

    def display_questions_for_editing(self, questions):
        """
        Displays the questions in a given category for editing.

        This method displays a table of questions within a given category and
        allows the user to select a question to edit. Once a question is selected,
        the user is prompted to edit the question, and the edited question is
        saved to the dataset.

        :param questions: The list of questions to display for editing.
        :return: None
        """
        if not questions:
            print("Немає запитань у цій категорії.")
            return

        table = Table(title="Оберіть запитання для редагування")
        table.add_column("№", justify="center")
        table.add_column("Запитання", justify="center")

        for idx, question in enumerate(questions, 1):
            table.add_row(str(idx), question["question"])

        self.console.print(table)

        question_choice = input(
            f"Оберіть запитання для редагування (1-{len(questions)}): "
        )
        try:
            question_choice = int(question_choice)
            if 1 <= question_choice <= len(questions):
                selected_question = questions[question_choice - 1]
                self.edit_question(selected_question, questions)
            else:
                print("Невірний вибір питання.")
        except ValueError:
            print("Невірний вибір.")

    def edit_question(self, question, all_questions):
        """
        Edits a given question within the dataset.

        This method allows the user to modify the text, options, and correct answers
        of a specified question. The updated question is then saved back into the
        overall list of questions.

        :param question: The question dictionary to be edited.
        :param all_questions: The list of all questions, used to update the specific
                              question with new data.
        :return: None
        """

        print(f"Редагуємо питання: {question['question']}")
        new_question_text = input("Введіть нове запитання: ")
        if new_question_text:
            question['question'] = new_question_text

        new_options = input("Введіть нові варіанти відповідей (через кому): ")
        if new_options:
            question['options'] = new_options.split(',')

        new_answers = input("Введіть нові правильні відповіді (через кому): ")
        if new_answers:
            question['correct_answers'] = new_answers.split(',')

        # Оновлюємо питання в списку
        for idx, q in enumerate(all_questions):
            if q['question'] == question['question']:
                all_questions[idx] = question

        self.quiz_data_manager.save_questions(all_questions)
        print("Питання було успішно змінено.")

    def view_quizzes(self):
        questions = self.quiz_data_manager.get_questions()
        if not questions:
            print("Немає запитань для перегляду.")
            return

        categories = self.get_unique_categories()
        if not categories:
            print("Немає доступних категорій для перегляду.")
            return

        for category in categories:
            print(f"\nКатегорія: {category}")
            questions_in_category = self.get_questions_by_category(category)

            table = Table(title=f"Запитання у категорії: {category}")
            table.add_column("№", justify="center")
            table.add_column("Запитання", justify="center")
            table.add_column("Варіанти відповідей", justify="center")
            table.add_column("Правильні відповіді", justify="center")

            for idx, question in enumerate(questions_in_category, 1):
                table.add_row(
                    str(idx), question["question"],
                    ", ".join(question["options"]),
                    ", ".join(question["correct_answers"])
                )

            self.console.print(table)

    def run(self):
        """
        Runs the Victorine utility menu, allowing the user to add, delete, edit,
        or view quizzes, as well as exit the application.

        This method continuously displays the Victorine utility menu to the user,
        allowing them to choose between adding a new quiz, deleting an existing
        quiz, editing an existing quiz, viewing all quizzes, or exiting the
        application. Based on the user's input, it directs them to the appropriate
        action. The loop continues until the user chooses to exit.

        User Options:
            1. Add a new quiz.
            2. Delete an existing quiz.
            3. Edit an existing quiz.
            4. View all quizzes.
            5. Exit the application.
        """
        while True:
            self.display_menu()
            choice = input("Оберіть опцію: ")

            if choice == "1":
                self.add_quiz()
            elif choice == "2":
                self.delete_quiz()
            elif choice == "3":
                self.edit_quiz()
            elif choice == "4":
                self.view_quizzes()
            elif choice == "5":
                print("До побачення!")
                break
            else:
                print("Невірний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    console = Console()
    quiz_data_manager = QuizDataManager()
    menu = VictorineUtilityMenu(quiz_data_manager, console)
    menu.run()
