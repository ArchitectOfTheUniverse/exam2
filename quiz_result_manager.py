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
        self.user_manager = user_manager

    def save_quiz_result(self, login, category, score):
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
        users = self.user_manager.load_user_data()
        return users.get(login, {}).get("quiz_results", {})

    def get_top_20(self, category):
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