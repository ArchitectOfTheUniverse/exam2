import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from user_manager import UserManager


@pytest.fixture
def mock_user_data():
    return {
        "user1": {
            "password": "password123",
            "birth_date": "1990-01-01",
            "quiz_results": {}
        }
    }


@pytest.fixture
def user_manager():
    with patch("user_manager.open", mock_open(read_data="{}")), patch("os.path.exists", return_value=True):
        return UserManager()


def test_initialize_user_data_creates_file_if_not_exists():
    with patch("os.path.exists", return_value=False), patch("builtins.open", mock_open()) as mock_file:
        UserManager()
        mock_file.assert_called_once_with(UserManager.USER_DATA_FILE, 'w')


def test_load_user_data_valid_data(user_manager, mock_user_data):
    with patch("user_manager.open", mock_open(read_data=json.dumps(mock_user_data))):
        data = user_manager.load_user_data()
        assert data == mock_user_data


def test_load_user_data_corrupted_file(user_manager):
    with (patch("user_manager.open", mock_open(read_data="INVALID_JSON")), patch("builtins.print") as mock_print,
          patch("user_manager.UserManager.save_user_data") as mock_save):
        data = user_manager.load_user_data()
        assert data == {}
        mock_print.assert_called_once()
        mock_save.assert_called_once_with({})


def test_save_user_data(user_manager, mock_user_data):
    with patch("user_manager.open", mock_open()) as mock_file:
        user_manager.save_user_data(mock_user_data)

        written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)

        assert written_data == json.dumps(mock_user_data, indent=4, ensure_ascii=False)


def test_register_user_success(user_manager, mock_user_data):
    with patch("user_manager.UserManager.load_user_data", return_value=mock_user_data), \
         patch("user_manager.UserManager.save_user_data") as mock_save, \
         patch("builtins.input", side_effect=["new_user", "secure_pass", "2000-01-01"]):
        login = user_manager.register_user()
        assert login == "new_user"
        mock_save.assert_called_once()


def test_register_user_existing_login(user_manager, mock_user_data):
    with patch("user_manager.UserManager.load_user_data", return_value=mock_user_data), \
         patch("builtins.input", side_effect=["user1"]):
        login = user_manager.register_user()
        assert login is None


def test_login_user_success(user_manager, mock_user_data):
    with patch("user_manager.UserManager.load_user_data", return_value=mock_user_data), \
         patch("builtins.input", side_effect=["user1", "password123"]), \
         patch("builtins.print") as mock_print:
        login = user_manager.login_user()
        assert login == "user1"
        mock_print.assert_any_call("\033[34mЛаскаво просимо, user1!\033[0m")


def test_login_user_invalid_password(user_manager, mock_user_data):
    with patch("user_manager.UserManager.load_user_data", return_value=mock_user_data), \
         patch("builtins.input", side_effect=["user1", "wrong_pass"]), \
         patch("builtins.print") as mock_print:
        login = user_manager.login_user()
        assert login is None
        mock_print.assert_any_call("\033[31mНевірний пароль.\033[0m")


def test_update_user_settings_success(user_manager, mock_user_data):
    with patch("user_manager.UserManager.load_user_data", return_value=mock_user_data), \
         patch("user_manager.UserManager.save_user_data") as mock_save, \
         patch("builtins.print") as mock_print:
        user_manager.update_user_settings("user1", "new_password", "2000-01-01")
        mock_save.assert_called_once()
        updated_data = mock_save.call_args[0][0]
        assert updated_data["user1"]["password"] == "new_password"
        assert updated_data["user1"]["birth_date"] == "2000-01-01"
        mock_print.assert_called_once_with("\033[32mНалаштування успішно оновлено!\033[0m")


def test_update_user_settings_user_not_found(user_manager, mock_user_data):
    with patch("user_manager.UserManager.load_user_data", return_value=mock_user_data), \
         patch("builtins.print") as mock_print:
        user_manager.update_user_settings("nonexistent_user", "new_password", "2000-01-01")
        mock_print.assert_called_once_with("\033[31mКористувача з таким логіном не існує.\033[0m")
