from typing import Dict, List, Tuple
from datetime import datetime
from user_manager import IUserManager
from abc import ABC, abstractmethod


class IQuizResultManager(ABC):
    @abstractmethod
    def save_quiz_result(self, login: str, category: str, score: int):
        pass

    @abstractmethod
    def get_user_results(self, login: str) -> Dict:
        pass

    @abstractmethod
    def get_top_20(self, category: str) -> List[Tuple[str, int, str]]:
        pass


class QuizResultManager(IQuizResultManager):
    def __init__(self, user_manager: IUserManager):
        """
        Initializes a QuizResultManager instance.

        Args:
            user_manager: An object implementing IUserManager, to manage users.
        """
        self.user_manager = user_manager

    def save_quiz_result(self, login, category, score):
        """
        Saves the quiz result for a user.

        This method saves the quiz result for a user. If the user doesn't have quiz results,
        a new entry is added to the user's data. If the user already has quiz results,
        the new result is appended to the existing list of results.

        Args:
            login (str): The login of the user whose quiz result is to be saved.
            category (str): The category of the quiz.
            score (int): The user's score in the quiz.
        """
        users = self.user_manager.load_user_data()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "category": category,
            "score": score,
            "date": now
        }

        if "quiz_results" not in users[login]:
            users[login]["quiz_results"] = {}

        if category not in users[login]["quiz_results"]:
            users[login]["quiz_results"][category] = []

        users[login]["quiz_results"][category].append(result)

        self.user_manager.save_user_data(users)

    def get_user_results(self, login):
        """
        Retrieve quiz results for a specific user.

        This method fetches the quiz results for the user identified by the given login.
        If the user has no quiz results, it returns an empty dictionary.

        Args:
            login (str): The login identifier of the user whose quiz results are to be retrieved.

        Returns:
            Dict: A dictionary containing the user's quiz results categorized by quiz category.
        """
        users = self.user_manager.load_user_data()
        return users.get(login, {}).get("quiz_results", {})

    def get_top_20(self, category):
        """
        Retrieve top 20 quiz results for a specific category.

        This method fetches the top 20 quiz results for the given category.
        If the category is "Змішана", it fetches the top 20 results from all categories.
        It returns a list of tuples, each containing the user's login, score and date of the quiz.

        Args:
            category (str): The category for which to retrieve the top 20 quiz results.

        Returns:
            List[Tuple[str, int, str]]: A list of tuples, each containing the user's login, score and date of the quiz.
        """
        users = self.user_manager.load_user_data()
        all_scores = []

        if category == "Змішана":
            for user, data in users.items():
                quiz_results = data.get("quiz_results", {})
                for cat, results in quiz_results.items():
                    for result in results:
                        all_scores.append(
                            (user, result['score'], result['date'])
                        )
        else:
            for user, data in users.items():
                quiz_results = data.get("quiz_results", {})
                if category in quiz_results:
                    for result in quiz_results[category]:
                        all_scores.append(
                            (user, result['score'], result['date'])
                        )

        all_scores.sort(key=lambda x: x[1], reverse=True)
        return all_scores[:20]