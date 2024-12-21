import pytest
from unittest.mock import MagicMock
from quiz_result_manager import QuizResultManager


@pytest.fixture
def mock_user_manager():
    mock_manager = MagicMock()
    mock_manager.load_user_data.return_value = {
        "user1": {
            "quiz_results": {
                "math": [
                    {"category": "math", "score": 80, "date": "2024-12-20 10:00:00"},
                    {"category": "math", "score": 90, "date": "2024-12-21 11:00:00"},
                ]
            }
        },
        "user2": {
            "quiz_results": {
                "science": [
                    {"category": "science", "score": 85, "date": "2024-12-19 09:00:00"}
                ]
            }
        },
    }
    return mock_manager


@pytest.fixture
def quiz_result_manager(mock_user_manager):
    return QuizResultManager(mock_user_manager)


def test_save_quiz_result_new_category(mock_user_manager, quiz_result_manager):
    mock_user_manager.load_user_data.return_value = {
        "user1": {"quiz_results": {}}
    }
    quiz_result_manager.save_quiz_result("user1", "geography", 70)
    mock_user_manager.save_user_data.assert_called_once()
    updated_data = mock_user_manager.save_user_data.call_args[0][0]
    assert "geography" in updated_data["user1"]["quiz_results"]
    assert len(updated_data["user1"]["quiz_results"]["geography"]) == 1
    assert updated_data["user1"]["quiz_results"]["geography"][0]["score"] == 70


def test_get_user_results(mock_user_manager, quiz_result_manager):
    results = quiz_result_manager.get_user_results("user1")
    assert "math" in results
    assert len(results["math"]) == 2
    assert results["math"][0]["score"] == 80


def test_get_user_results_no_results(mock_user_manager, quiz_result_manager):
    mock_user_manager.load_user_data.return_value = {"user3": {}}
    results = quiz_result_manager.get_user_results("user3")
    assert results == {}


def test_get_top_20_specific_category(mock_user_manager, quiz_result_manager):
    top_scores = quiz_result_manager.get_top_20("math")
    assert len(top_scores) == 2
    assert top_scores[0][1] == 90
    assert top_scores[1][1] == 80


def test_get_top_20_mixed_category(mock_user_manager, quiz_result_manager):
    top_scores = quiz_result_manager.get_top_20("Змішана")
    assert len(top_scores) == 3
    assert top_scores[0][1] == 90
    assert top_scores[1][1] == 85
    assert top_scores[2][1] == 80


def test_save_quiz_result_existing_category(mock_user_manager, quiz_result_manager):
    quiz_result_manager.save_quiz_result("user1", "math", 95)
    mock_user_manager.save_user_data.assert_called_once()
    updated_data = mock_user_manager.save_user_data.call_args[0][0]
    assert len(updated_data["user1"]["quiz_results"]["math"]) == 3
    assert updated_data["user1"]["quiz_results"]["math"][-1]["score"] == 95
