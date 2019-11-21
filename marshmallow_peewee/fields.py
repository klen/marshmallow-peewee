import datetime as dt

from marshmallow import fields, ValidationError


class Timestamp(fields.Field):

    default_error_messages = {
        'invalid': 'Not a valid timestamp.'
    }

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize given datetime to timestamp."""
        if value is None:
            return None

        return int(datetime_to_timestamp(value))

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:  # Falsy values, e.g. '', None, [] are not valid
            raise self.make_error('invalid')

        try:
            return dt.datetime.utcfromtimestamp(float(value))
        except ValueError:
            raise self.make_error('invalid')


class MSTimestamp(Timestamp):

    def _serialize(self, value, *args, **kwargs):
        """Serialize given datetime to timestamp."""
        if value is not None:
            value = super(MSTimestamp, self)._serialize(value, *args) * 1e3
        return value

    def _deserialize(self, value, *args, **kwargs):
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

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            return int(value)

        return super(Related, self)._deserialize(value, attr, data)


class ForeignKey(fields.Raw):

    def get_value(self, obj, attr, **kwargs):
        """Return the value for a given key from an object."""
        value = obj.__data__.get(attr)
        if self.root and self.root.opts.string_keys and value is not None:
            value = str(value)
        return value


class StringRelatedField(Related):

    def __init__(self, deserialize=None, *args, **kwargs):
        """
        :param deserialize: A callable from which to retrieve the value.
                            The function must take a two arguments, first model,
                            which is the model of the deserialized type and
                            value, which is the value to be deserialized.
                            If no callable is provided then the field is read-only.
        """
        self._deserialize_function = deserialize
        super(StringRelatedField, self).__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if self._deserialize_function is None:
            raise AttributeError('"{}" is a read-only attribute and can not be serialized. '
                                 'Use the "deserialize" attribute to enable deserialization.'
                                 .format(attr))
        model = self.schema.Meta.model
        val = self._deserialize_function(model, value)
        if not isinstance(val, model):
            raise ValidationError('Deserialized object of "{}" is not of type {}'
                                  .format(attr, model.__name__))
        return val

    def _serialize(self, nested_obj, attr, obj):
        return str(nested_obj)


def datetime_to_timestamp(dt_):
    """Convert given datetime object to timestamp in seconds."""
    return dt_.replace(tzinfo=dt.timezone.utc).timestamp()
