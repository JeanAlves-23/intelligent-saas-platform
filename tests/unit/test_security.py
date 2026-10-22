from app.core.security import hash_password, verify_password


def test_hash_password() -> None:
    password = "SecurePassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")


def test_verify_correct_password() -> None:
    password = "SecurePassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_reject_incorrect_password() -> None:
    hashed = hash_password("CorrectPassword123!")

    assert verify_password("WrongPassword123!", hashed) is False


def test_same_password_generates_different_hashes() -> None:
    password = "SecurePassword123!"

    first = hash_password(password)
    second = hash_password(password)

    assert first != second

    assert verify_password(password, first) is True
    assert verify_password(password, second) is True
