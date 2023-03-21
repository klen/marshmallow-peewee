from __future__ import annotations

from collections.abc import Callable
from typing import List, Tuple, Type, TypeVar

import marshmallow as ma
import peewee as pw

TVModel = TypeVar("TVModel", bound=pw.Model)
TFieldMappingList = List[Tuple[Type[pw.Field], Callable[..., ma.fields.Field]]]
