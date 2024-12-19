from user_manager import UserManager
from quiz_result_manager import QuizResultManager
from quiz_loader import QuizLoader
from quiz_orchestrator import QuizOrchestrator


class QuizApp:
    def __init__(self):
        """
        Initializes the QuizApp class, setting up the user manager, result manager,
        quiz loader, and quiz orchestrator components necessary for the application
        to function. These components are responsible for managing users, handling quiz
        results, loading quiz data, and orchestrating the overall quiz flow.
        """
        self.user_manager = UserManager()
        self.result_manager = QuizResultManager(self.user_manager)
        self.quiz_loader = QuizLoader()
        self.quiz_orchestrator = QuizOrchestrator(
            self.user_manager, self.result_manager, self.quiz_loader
        )
        # self.victorine_utility = VictorineUtilityMenu()

    def run(self):
        """
        Runs the quiz application, launching the main menu where users can log in,
        register, or exit the application.
        """
        self.quiz_orchestrator.main_menu()


if __name__ == "__main__":
    app = QuizApp()
    app.run()
