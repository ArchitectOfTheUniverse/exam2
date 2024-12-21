import pytest
import json
import os
from unittest.mock import Mock, patch
from rich.console import Console
from rich.table import Table
from victorine_utility import QuizDataManager, VictorineUtilityMenu


@pytest.fixture
def temp_json_file(tmp_path):
    file_path = tmp_path / "test_questions.json"
    test_data = {
        "questions": [
            {
                "category": "Math",
                "question": "2 + 2 = ?",
                "options": ["3", "4", "5"],
                "correct_answers": ["4"]
            },
            {
                "category": "History",
                "question": "First president of Ukraine?",
                "options": ["Kravchuk", "Kuchma", "Yushchenko"],
                "correct_answers": ["Kravchuk"]
            }
        ]
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
    return file_path


@pytest.fixture
def quiz_data_manager(temp_json_file):
    return QuizDataManager(temp_json_file)


@pytest.fixture
def victorine_menu(quiz_data_manager):
    console = Console()
    return VictorineUtilityMenu(quiz_data_manager, console)


class TestQuizDataManager:
    def test_get_questions_success(self, quiz_data_manager):
        questions = quiz_data_manager.get_questions()
        assert len(questions) == 2
        assert questions[0]["category"] == "Math"
        assert questions[1]["category"] == "History"

    def test_get_questions_file_not_found(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.json"
        manager = QuizDataManager(str(nonexistent_file))
        assert manager.get_questions() == []

    def test_save_questions_success(self, quiz_data_manager, temp_json_file):
        new_questions = [{
            "category": "Science",
            "question": "What is H2O?",
            "options": ["Water", "Air", "Fire"],
            "correct_answers": ["Water"]
        }]
        quiz_data_manager.save_questions(new_questions)

        with open(temp_json_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            assert len(saved_data["questions"]) == 1
            assert saved_data["questions"][0]["category"] == "Science"


class TestVictorineUtilityMenu:
    def test_get_unique_categories(self, victorine_menu):
        categories = victorine_menu.get_unique_categories()
        assert len(categories) == 2
        assert "Math" in categories
        assert "History" in categories

    def test_get_questions_by_category(self, victorine_menu):
        math_questions = victorine_menu.get_questions_by_category("Math")
        assert len(math_questions) == 1
        assert math_questions[0]["question"] == "2 + 2 = ?"

    @patch('builtins.input')
    def test_add_quiz(self, mock_input, victorine_menu):
        mock_input.side_effect = [
            "Science",
            "What is gravity?",
            "Force,Energy,Mass",
            "Force",
            "n"
        ]

        victorine_menu.add_quiz()
        questions = victorine_menu.quiz_data_manager.get_questions()

        science_questions = [q for q in questions if q["category"] == "Science"]
        assert len(science_questions) == 1
        assert science_questions[0]["question"] == "What is gravity?"

    def test_display_menu(self, victorine_menu):
        victorine_menu.display_menu()
        assert True


if __name__ == "__main__":
    pytest.main(["-v"])