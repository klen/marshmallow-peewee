from datetime import datetime, timezone

from marshmallow.compat import PY2
from marshmallow.fields import Field


class Timestamp(Field):

    def _serialize(self, value, attr, obj):
        """Serialize given datetime to timestamp."""
        if value is None:
            return None

        return int(datetime_to_timestamp(value))

    def _deserialize(self, value, attr, data):
        if not value:  # Falsy values, e.g. '', None, [] are not valid
            raise self.fail('invalid')

        try:
            return datetime.utcfromtimestamp(float(value))
        except ValueError:
            raise self.fail('invalid')


if PY2:
    def datetime_to_timestamp(dt, epoch=datetime(1979, 1, 1)):
        """Convert given datetime object to timestamp in seconds."""
        return (dt - epoch).total_seconds()

else:

    def datetime_to_timestamp(dt):
        """Convert given datetime object to timestamp in seconds."""
        return dt.replace(tzinfo=timezone.utc).timestamp()
