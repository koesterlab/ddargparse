from dataclasses import Field
from typing import Never


def _raise_invalid(message: str, cls_field: Field) -> Never:
    raise ValueError(f"{message} Invalid field: {cls_field.name}")
