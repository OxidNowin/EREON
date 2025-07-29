from typing import Type, TypeVar, get_origin, get_args
from dataclasses import is_dataclass, fields
from enum import Enum

T = TypeVar("T")

def from_dict(data_class: Type[T], data: dict) -> T:
    if not is_dataclass(data_class):
        raise TypeError(f"{data_class} is not a dataclass")

    kwargs = {}
    for f in fields(data_class):
        value = data.get(f.name)

        if value is None:
            kwargs[f.name] = None
            continue

        field_type = f.type
        origin = get_origin(field_type)
        args = get_args(field_type)

        if origin is list and args:
            item_type = args[0]
            if is_dataclass(item_type):
                kwargs[f.name] = [from_dict(item_type, item) for item in value]
            else:
                kwargs[f.name] = value

        elif is_dataclass(field_type):
            kwargs[f.name] = from_dict(field_type, value)

        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            kwargs[f.name] = field_type(value)

        else:
            kwargs[f.name] = value

    return data_class(**kwargs)
