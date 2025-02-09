import json
import os
from typing import List, Dict
from abc import ABC, abstractmethod
from colorama import Fore, Style


class IQuizLoader(ABC):
    @abstractmethod
    def load_questions(self) -> List[Dict]:
        """
        Loads questions from a json file.

        Returns:
            List[Dict]: List of questions.
        """
        pass


class QuizLoader(IQuizLoader):
    def load_questions(self) -> List[Dict]:
        """
        Loads questions from a json file.

        If the file is not found, returns an empty list and prints a message.

        Returns:
            List[Dict]: List of questions.
        """
        if not os.path.exists("questions.json"):
            print(
                f"{Fore.RED}Файл з запитаннями не знайдено!{Style.RESET_ALL}"
            )
            return []

        with open("questions.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data["questions"]