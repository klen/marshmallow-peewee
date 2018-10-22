import datetime as dt

from marshmallow import fields

from .compat import PY2, string_types


class Timestamp(fields.Field):

    default_error_messages = {
        'invalid': 'Not a valid timestamp.'
    }

    def _serialize(self, value, attr, obj):
        """Serialize given datetime to timestamp."""
        if value is None:
            return None

        return int(datetime_to_timestamp(value))

    def _deserialize(self, value, attr, data):
        if not value:  # Falsy values, e.g. '', None, [] are not valid
            raise self.fail('invalid')

        try:
            return dt.datetime.utcfromtimestamp(float(value))
        except ValueError:
            raise self.fail('invalid')


class MSTimestamp(Timestamp):

    def _serialize(self, value, *args):
        """Serialize given datetime to timestamp."""
        if value is not None:
            value = super(MSTimestamp, self)._serialize(value, *args) * 1e3
        return value

    def _deserialize(self, value, *args):
        if value:
            value = int(value) / 1e3

        return super(MSTimestamp, self)._deserialize(value, *args)


class Related(fields.Nested):

    def __init__(self, nested=None, meta=None, **kwargs):
        self.meta = meta or {}
        super(Related, self).__init__(nested, **kwargs)

    def init_model(self, model, name):
        from .schema import ModelSchema
        field = model._meta.fields.get(name)

        if not field:
            field = getattr(model, name, None).field
            self.many = True
            rel_model = field.model
        else:
            rel_model = field.rel_model

        self.attribute = self.attribute or name
        self.meta['model'] = rel_model
        meta = type('Meta', (), self.meta)
        self.nested = type('Schema', (ModelSchema,), {'Meta': meta})

    def _deserialize(self, value, attr, data):
        if isinstance(value, (int, string_types)):
            return int(value)
        return super(Related, self)._deserialize(value, attr, data)


class ForeignKey(fields.Raw):

    def get_value(self, attr, obj, *args, **kwargs):
        """Return the value for a given key from an object."""
        value = obj.__data__.get(attr)
        if value is not None:
            value = str(value)
        return value


if PY2:
    def datetime_to_timestamp(dt_, epoch=dt.datetime(1970, 1, 1)):
        """Convert given datetime object to timestamp in seconds."""
        return (dt_ - epoch).total_seconds()

else:

    def datetime_to_timestamp(dt_):
        """Convert given datetime object to timestamp in seconds."""
        return dt_.replace(tzinfo=dt.timezone.utc).timestamp()
