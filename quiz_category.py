import random
from typing import List, Dict
from abc import ABC, abstractmethod
from colorama import Fore, Style


class IQuizCategory(ABC):
    @abstractmethod
    def load_questions(self):
        pass

    @abstractmethod
    def get_questions(self) -> List[Dict]:
        pass


class QuizCategory(IQuizCategory):
    def __init__(self, questions: List[Dict]):
        self.questions = questions

    def load_questions(self):
        pass

    def get_questions(self) -> List[Dict]:
        pass


class MixedCategory(QuizCategory):
    def __init__(self, questions: List[Dict]):
        super().__init__(questions)

    def load_questions(self) -> List[Dict]:
        return self.questions

    def get_questions(self) -> List[Dict]:
        return random.sample(self.questions, 20)


class SpecificCategory(QuizCategory):
    def __init__(self, questions: List[Dict], category: str):
        super().__init__(questions)
        self.category = category
        self.questions = [
            question for question in questions
            if question["category"].lower() == self.category
        ]

    def load_questions(self) -> List[Dict]:
        if len(self.questions) < 20:
            print(
                f"{Fore.RED}"
                f"У категорії {self.category} недостатньо питань."
                f"Вибрано лише {len(self.questions)} питань"
                f"{Style.RESET_ALL}"
            )
        return self.questions

    def get_questions(self) -> List[Dict]:
        return random.sample(self.questions, min(20, len(self.questions)))












