registration_data = {
    "login": "Test",
    "email": "test.user@example.com",
    "password": "password",
    "first_name": "Test",
    "last_name": "Test",
}

change_login_data = {
    "password_data": {"user_login": "Test", "password": "password"},
    "password_change_data": {"new_login": "Test-1", "new_password": "Test-1"},
}

change_login_wrong_data = {
    "password_data": {"user_login": "Tests", "password": "passwordd"},
    "password_change_data": {"new_login": "Test-1", "new_password": "Test-1"},
}

only_login_data = {
    "password_data": {"user_login": "Test", "password": "password"},
    "password_change_data": {"new_login": "new_login"},
}

only_login_data_wrong = {
    "password_data": {"user_login": "Tests", "password": "password"},
    "password_change_data": {"new_login": "new_login"},
}

only_password_data = {
    "password_data": {"user_login": "Test", "password": "password"},
    "password_change_data": {"new_password": "Test-1"},
}

only_password_data_wrong = {
    "password_data": {"user_login": "Test", "password": "passwords"},
    "password_change_data": {"new_password": "Test-1"},
}
