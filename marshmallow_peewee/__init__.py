__license__ = "MIT"
__project__ = "Marshmallow-Peewee"
__version__ = "2.3.0"

import marshmallow as ma

MA_VERSION = ma.__version__.split('.')

from .schema import ModelSchema # noqa
from .fields import Timestamp, MSTimestamp, Related, ForeignKey # noqa
