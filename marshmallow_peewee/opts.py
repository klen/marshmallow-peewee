from __future__ import annotations

DEFAULTS = {
    "dump_only_pk": True,
    "string_keys": True,
    "id_keys": False,
}


def setup(**options):
    """Setup marshmallow-peewee defaults."""
    DEFAULTS.update(options)
