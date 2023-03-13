from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from marshmallow import Schema, fields

if TYPE_CHECKING:
    import peewee as pw


class Related(fields.Nested):
    def __init__(
        self,
        nested: Optional[Schema] = None,
        meta: Optional[Dict] = None,
        **kwargs,
    ):
        self.field = None
        self.meta = meta or {}
        super(Related, self).__init__(nested, **kwargs)  # type: ignore[arg-type]

    def init_model(self, model: pw.Model, name: str):
        from .schema import ModelSchema

        field = model._meta.fields.get(name)
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

    def get_value(self, obj: pw.Model, *_, **__) -> Any:
        """Return the value for a given key from an object."""
        value = obj.__data__.get(self.attribute)
        if value is not None and self.string_keys:
            return str(value)
        return value
