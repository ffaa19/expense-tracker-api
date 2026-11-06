from security import hash_password, verify_password


def test_password_hashing():
    password = "MyPassword123"

    # Hash the password
    hashed_password = hash_password(password)

    # The hash should not equal the original password
    assert hashed_password != password

    # The correct password should be verified
    assert verify_password(password, hashed_password) is True

    # An incorrect password should not be verified
    assert verify_password("WrongPassword", hashed_password) is False