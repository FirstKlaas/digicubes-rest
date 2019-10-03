"""
My own fields
"""
from datetime import datetime


def base_converter(info, field, val):
    """
    Standard converter for None values and
    int, str, float values. Also supports
    datetime. Datetime value are converted
    using the isoformat() method.
    """
    if val is None or isinstance(val, (int, str, float)):
        return val

    if isinstance(val, datetime):
        return val.isoformat()

    raise ValueError(f"Unsupported  value type <{type(val)}>")
