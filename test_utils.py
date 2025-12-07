import utils

def test_try_int_or_zero_valid():
    assert utils.try_int_or_zero("123") == 123


def test_try_int_or_zero_invalid():
    assert utils.try_int_or_zero("abc") == 0
    assert utils.try_int_or_zero("") == 0
    assert utils.try_int_or_zero(None) == 0


def test_validate_password_strength_ok():
    ok, msg = utils.validate_password_strength("StrongPass1")
    assert ok is True
    assert msg == "OK"


def test_validate_password_strength_too_short():
    ok, msg = utils.validate_password_strength("S1a")
    assert ok is False
    assert "at least 8" in msg


def test_validate_password_strength_missing_upper():
    ok, msg = utils.validate_password_strength("lowercase1")
    assert ok is False
    assert "uppercase" in msg.lower()


def test_hash_and_verify_password_roundtrip():
    pw = "StrongPass1"
    salt_hex, hash_hex = utils.hash_password(pw)
    assert salt_hex  # not empty
    assert hash_hex

    assert utils.verify_password(pw, salt_hex, hash_hex) is True
    assert utils.verify_password("WrongPass", salt_hex, hash_hex) is False
