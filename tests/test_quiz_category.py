import pytest
from quiz_category import MixedCategory, SpecificCategory


@pytest.fixture
def sample_questions():
    return [
        {"question": "What is the capital of France?", "category": "geography"},
        {"question": "What is 2 + 2?", "category": "math"},
        {"question": "Who wrote 'Hamlet'?", "category": "literature"},
        {"question": "What is the boiling point of water?", "category": "science"},
        {"question": "What is the capital of Germany?", "category": "geography"},
        {"question": "What is 5 * 6?", "category": "math"},
        {"question": "Who wrote '1984'?", "category": "literature"},
    ]


def test_mixed_category_load_questions(sample_questions):
    category = MixedCategory(sample_questions)
    loaded_questions = category.load_questions()
    assert loaded_questions == sample_questions


def test_mixed_category_get_questions(sample_questions):
    category = MixedCategory(sample_questions)
    questions = category.get_questions()
    assert len(questions) <= 20
    assert all(question in sample_questions for question in questions)


def test_specific_category_load_questions(sample_questions):
    category = SpecificCategory(sample_questions, "geography")
    loaded_questions = category.load_questions()
    expected_questions = [
        {"question": "What is the capital of France?", "category": "geography"},
        {"question": "What is the capital of Germany?", "category": "geography"},
    ]
    assert loaded_questions == expected_questions


def test_specific_category_get_questions(sample_questions):
    category = SpecificCategory(sample_questions, "geography")
    questions = category.get_questions()
    assert len(questions) <= 20
    assert all(question["category"].lower() == "geography" for question in questions)


def test_specific_category_warning_on_few_questions(capfd, sample_questions):
    category = SpecificCategory(sample_questions, "literature")
    category.load_questions()
    captured = capfd.readouterr()
    assert "У категорії literature недостатньо питань." in captured.out
