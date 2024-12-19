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
        self.file_path = file_path

    def get_questions(self):
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
        table = Table(title="Меню вікторин")
        table.add_column()
        table.add_column()

        for key, value in self.menu.items():
            table.add_row(key, value)

        self.console.print(table)

    def get_unique_categories(self):
        questions = self.quiz_data_manager.get_questions()
        categories = set()

        for question in questions:
            if "category" in question:
                categories.add(question["category"])

        return sorted(categories)

    def get_questions_by_category(self, category):
        questions = self.quiz_data_manager.get_questions()
        return [q for q in questions if q["category"] == category]

    def delete_quiz(self):
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
        questions = self.quiz_data_manager.get_questions()
        filtered_questions = [
            q for q in questions if q["category"] != category
        ]

        self.quiz_data_manager.save_questions(filtered_questions)
        print(f"Усі запитання з категорії '{category}' були видалені.")

    def add_quiz(self):
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
