"""Unit tests for application.py."""

from application import TestMe


def test_server():
    """Check that take_five returns 5."""
    assert TestMe().take_five() == 5


def test_port():
    """Check application port."""
    assert TestMe().port() == 8000
