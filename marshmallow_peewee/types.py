from __future__ import annotations

from collections.abc import Callable
from typing import List, Tuple, Type

import marshmallow as ma
import peewee as pw

TFieldMappingList = List[Tuple[Type[pw.Field], Callable[..., ma.fields.Field]]]
