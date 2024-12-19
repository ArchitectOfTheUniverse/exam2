from user_manager import UserManager
from quiz_result_manager import QuizResultManager
from quiz_loader import QuizLoader
from quiz_orchestrator import QuizOrchestrator


class QuizApp:
    def __init__(self):
        self.user_manager = UserManager()
        self.result_manager = QuizResultManager(self.user_manager)
        self.quiz_loader = QuizLoader()
        self.quiz_orchestrator = QuizOrchestrator(
            self.user_manager, self.result_manager, self.quiz_loader
        )
        # self.victorine_utility = VictorineUtilityMenu()

    def run(self):
        self.quiz_orchestrator.main_menu()


if __name__ == "__main__":
    app = QuizApp()
    app.run()
