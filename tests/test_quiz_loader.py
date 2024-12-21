import os
import json
import pytest
from unittest.mock import patch, mock_open
from quiz_loader import QuizLoader


@pytest.fixture
def quiz_loader():
    return QuizLoader()


def test_load_questions_file_exists(quiz_loader):
    mock_data = {"questions": [{"question": "Test question?", "answer": "Test answer"}]}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        with patch("os.path.exists", return_value=True):
            questions = quiz_loader.load_questions()
            assert questions == mock_data["questions"]


def test_load_questions_file_not_found(quiz_loader):
    with patch("os.path.exists", return_value=False):
        with patch("builtins.print") as mock_print:
            questions = quiz_loader.load_questions()
            assert questions == []
            mock_print.assert_called_with("\x1b[31mФайл з запитаннями не знайдено!\x1b[0m")


def test_load_questions_invalid_data(quiz_loader):
    invalid_data = "invalid json"
    with patch("builtins.open", mock_open(read_data=invalid_data)):
        with patch("os.path.exists", return_value=True):
            with pytest.raises(json.JSONDecodeError):
                quiz_loader.load_questions()
