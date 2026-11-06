from security import create_access_token


def test_create_access_token():
    token = create_access_token({"sub": "1"})

    assert isinstance(token, str)
    assert len(token) > 0