import pytest
import re
from unittest.mock import MagicMock
from rich.console import Console
from quiz_orchestrator import QuizOrchestrator


def remove_ansi_codes(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


@pytest.fixture
def mock_dependencies():
    user_manager = MagicMock()
    result_manager = MagicMock()
    quiz_loader = MagicMock()
    quiz_data_manager = MagicMock()

    return {
        "user_manager": user_manager,
        "result_manager": result_manager,
        "quiz_loader": quiz_loader,
        "quiz_data_manager": quiz_data_manager,
    }


@pytest.fixture
def orchestrator(mock_dependencies):
    return QuizOrchestrator(
        user_manager=mock_dependencies["user_manager"],
        result_manager=mock_dependencies["result_manager"],
        quiz_loader=mock_dependencies["quiz_loader"],
        console=Console(),
        quiz_data_manager=mock_dependencies["quiz_data_manager"],
    )


def test_display_main_menu(orchestrator, capsys):
    orchestrator.display_main_menu()
    captured = capsys.readouterr()
    assert "Головне меню" in captured.out
    assert "1" in captured.out
    assert "Вхід" in captured.out
    assert "2" in captured.out
    assert "Реєстрація" in captured.out
    assert "3" in captured.out
    assert "Вихід" in captured.out


def test_display_user_menu(orchestrator, capsys):
    orchestrator.display_user_menu(is_admin=False)
    captured = capsys.readouterr()
    assert "Меню користувача" in captured.out
    assert "1" in captured.out
    assert "Стартувати нову вікторину" in captured.out
    assert "5" in captured.out
    assert "Вихід" in captured.out
    assert "Редагування" not in captured.out

    orchestrator.display_user_menu(is_admin=True)
    captured = capsys.readouterr()
    assert "Редагування" in captured.out


def test_get_unique_categories(orchestrator, mock_dependencies):
    mock_dependencies["quiz_loader"].load_questions.return_value = [
        {"category": "math", "question": "Q1", "options": ["A", "B"], "correct_answers": ["A"]},
        {"category": "science", "question": "Q2", "options": ["C", "D"], "correct_answers": ["C"]},
    ]
    categories = orchestrator.get_unique_categories()
    assert categories == ["math", "science"]


def test_start_quiz(orchestrator, mock_dependencies, monkeypatch):
    mock_dependencies["quiz_loader"].load_questions.return_value = [
        {"category": "math", "question": "Q1", "options": ["A", "B"], "correct_answers": ["A"]},
    ]

    inputs = iter(["1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    orchestrator.start_quiz("test_user", "math")
    mock_dependencies["result_manager"].save_quiz_result.assert_called_once_with("test_user", "math", 1)


def test_display_results(orchestrator, mock_dependencies, capsys):
    mock_dependencies["result_manager"].get_user_results.return_value = {
        "math": [{"date": "2024-01-01", "score": 5}],
        "science": [{"date": "2024-01-02", "score": 3}],
    }

    orchestrator.display_results("test_user")
    captured = capsys.readouterr()

    output = remove_ansi_codes(captured.out).strip()

    assert re.search(r"Перегляд результатів для користувача test_user", output)
    assert re.search(r"Результати для\s*категорії\s*math", output)
    assert re.search(r"2024-01-01", output)
    assert re.search(r"5", output)
    assert re.search(r"Результати для\s*категорії\s*science", output)
    assert re.search(r"2024-01-02", output)
    assert re.search(r"3", output)

    assert re.search(r"┌────────────┬───────┐", output)
    assert re.search(r"├────────────┼───────┤", output)
    assert re.search(r"└────────────┴───────┘", output)


def test_display_top_20(orchestrator, mock_dependencies, capsys):
    mock_dependencies["result_manager"].get_top_20.return_value = [
        ("user1", 10, "2024-01-01"),
        ("user2", 8, "2024-01-02"),
    ]

    orchestrator.display_top_20("math")
    captured = capsys.readouterr()
    assert "Топ-20 для категорії math" in captured.out
    assert "user1" in captured.out
    assert "10" in captured.out
    assert "2024-01-01" in captured.out


def test_user_menu_exit(orchestrator, monkeypatch, capsys):
    inputs = iter(["5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    orchestrator.user_menu("test_user")
    captured = capsys.readouterr()
    assert "Вихід із програми" in captured.out
