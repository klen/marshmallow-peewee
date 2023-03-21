from __future__ import annotations

from typing import Final

DEFAULTS: Final = {
    "dump_only_pk": True,
    "string_keys": True,
    "id_keys": False,
}


def setup(**options):
    """Setup marshmallow-peewee defaults."""
    DEFAULTS.update(options)
