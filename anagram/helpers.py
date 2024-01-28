from django.forms import NullBooleanField


def to_python_bool(value: str | bool | None) -> bool:
    """Convert a value to a boolean value. Convenient to parse request query parameters."""
    return NullBooleanField().to_python(value)


def calculate_median(lengths: list[int]) -> float | None:
    if not lengths:
        return None

    count = len(lengths)
    if count % 2 == 1:
        return lengths[count // 2]
    else:
        return (lengths[count // 2 - 1] + lengths[count // 2]) / 2
