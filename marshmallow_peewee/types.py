from __future__ import annotations

from typing import Callable, Tuple, TypeVar

import marshmallow as ma
import peewee as pw

TVModel = TypeVar("TVModel", bound=pw.Model)
TFieldMappingList = list[Tuple[type[pw.Field], Callable[..., ma.fields.Field]]]
