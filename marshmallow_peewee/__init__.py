__version__ = "3.4.3"

DEFAULTS = {
    "dump_only_pk": True,
    "string_keys": True,
    "id_keys": False,
}

from .fields import ForeignKey, MSTimestamp, Related, Timestamp
from .schema import ModelSchema


def setup(**options):
    """Setup marshmallow-peewee defaults."""
    DEFAULTS.update(options)


__all__ = "ModelSchema", "Timestamp", "MSTimestamp", "Related", "ForeignKey", "setup"
