from django.forms import NullBooleanField


def to_python_bool(value: str | bool | None) -> bool:
    """Convert a value to a boolean value. Convenient to parse request query parameters."""
    return NullBooleanField().to_python(value)
