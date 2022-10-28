import datetime as dt
import typing as t

import peewee as pw
from marshmallow import Schema, fields


class Timestamp(fields.Field):

    default_error_messages = {"invalid": "Not a valid timestamp."}

    def _serialize(
        self, value: dt.datetime, attr: t.Optional[str], obj: pw.Model, **kwargs
    ) -> t.Optional[int]:
        """Serialize given datetime to timestamp."""
        if value is None:
            return None

        return int(value.timestamp())

    def _deserialize(
        self,
        value: t.Union[str, int, float],
        attr: t.Optional[str],
        data: t.Optional[t.Mapping[str, t.Any]],
        **kwargs,
    ) -> dt.datetime:
        if not value:  # Falsy values, e.g. '', None, [] are not valid
            raise self.make_error("invalid")

        try:
            return dt.datetime.utcfromtimestamp(float(value))
        except ValueError:
            raise self.make_error("invalid")


class MSTimestamp(Timestamp):
    def _serialize(
        self, value: dt.datetime, attr: t.Optional[str], obj: pw.Model, *_, **__
    ) -> t.Optional[int]:
        """Serialize given datetime to timestamp."""
        val = super(MSTimestamp, self)._serialize(value, attr, obj)
        if val is None:
            return None

        return val * 1000

    def _deserialize(
        self,
        value: t.Union[str, int, float],
        attr: t.Optional[str],
        data: t.Optional[t.Mapping[str, t.Any]],
        **_,
    ) -> dt.datetime:
        if value:
            value = int(value) / 1e3

        return super(MSTimestamp, self)._deserialize(value, attr, data)


class Related(fields.Nested):
    def __init__(self, nested: Schema = None, meta: t.Dict = None, **kwargs):  # type: ignore
        self.field = None
        self.meta = meta or {}
        super(Related, self).__init__(nested, **kwargs)  # type: ignore

    def init_model(self, model: pw.Model, name: str):
        from .schema import ModelSchema

        field = model._meta.fields.get(name)  # type: ignore
        if not field:
            field = getattr(model, name).field
            self.many = True
            rel_model = field.model
        else:
            rel_model = field.rel_model

        self.field = field
        self.attribute = self.attribute or name
        self.meta["model"] = rel_model
        meta = type("Meta", (), self.meta)
        self.nested = type("Schema", (ModelSchema,), {"Meta": meta})

    def _deserialize(self, value, attr, data, **_):
        if self.field is None:
            raise RuntimeError("Init model first.")

        if not isinstance(value, dict):
            return self.field.rel_field.python_value(value)

        return super(Related, self)._deserialize(value, attr, data)


class ForeignKey(fields.Raw):
    string_keys = False

    def _bind_to_schema(self, field_name, schema):
        self.string_keys = schema.opts.string_keys
        super()._bind_to_schema(field_name, schema)

    def get_value(self, obj: pw.Model, attr: str, **_) -> t.Any:  # type: ignore
        """Return the value for a given key from an object."""
        value = obj.__data__.get(self.attribute)
        if value is not None and self.string_keys:
            value = str(value)
        return value
