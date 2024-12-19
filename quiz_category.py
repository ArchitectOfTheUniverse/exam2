import random
from typing import List, Dict
from abc import ABC, abstractmethod
from colorama import Fore, Style


class IQuizCategory(ABC):
    @abstractmethod
    def load_questions(self):
        """
        Loads questions from a source and assigns them to the category.

        This method is abstract and should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_questions(self) -> List[Dict]:
        """
        Retrieves the list of questions assigned to the category.

        Returns:
            List[Dict]: A list of dictionaries, each representing a question.
        """
        pass


class QuizCategory(IQuizCategory):
    def __init__(self, questions: List[Dict]):
        """
        Initializes a QuizCategory with a list of questions.

        Args:
            questions (List[Dict]): A list of dictionaries, each representing a question.
        """
        self.questions = questions

    def load_questions(self):
        """
        Loads questions from a source and assigns them to the category.

        This is a default implementation that does nothing. Subclasses should
        override this method to load questions from a specific source.
        """
        pass

    def get_questions(self) -> List[Dict]:
        """
        Retrieves a list of questions assigned to this category.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary represents a question.
        """
        pass


class MixedCategory(QuizCategory):
    def __init__(self, questions: List[Dict]):
        """
        Initializes a MixedCategory with a list of questions.

        Args:
            questions (List[Dict]): A list of dictionaries, each representing a question.
        """
        super().__init__(questions)

    def load_questions(self) -> List[Dict]:
        return self.questions

    def get_questions(self) -> List[Dict]:
        return random.sample(self.questions, 20)


class SpecificCategory(QuizCategory):
    def __init__(self, questions: List[Dict], category: str):
        """
        Initializes a SpecificCategory with a list of questions and a category.

        Args:
            questions (List[Dict]): A list of dictionaries, each representing a question.
            category (str): Category name as a string.

        """
        super().__init__(questions)
        self.category = category
        self.questions = [
            question for question in questions
            if question["category"].lower() == self.category
        ]

    def load_questions(self) -> List[Dict]:
        """
        Loads and returns questions specific to the category.

        If the number of questions in the category is less than 20,
        a warning message is printed indicating the shortage of questions.

        Returns:
            List[Dict]: A list of dictionaries, each representing a question in the category.
        """
        if len(self.questions) < 20:
            print(
                f"{Fore.RED}"
                f"У категорії {self.category} недостатньо питань."
                f"Вибрано лише {len(self.questions)} питань"
                f"{Style.RESET_ALL}"
            )
        return self.questions

    def get_questions(self) -> List[Dict]:
        """
        Retrieves a list of up to 20 random questions specific to the category.

        Returns:
            List[Dict]: A list of dictionaries, each representing a question
            in the category. The length of the list is at most 20, depending
            on the number of available questions.
        """
        return random.sample(self.questions, min(20, len(self.questions)))












