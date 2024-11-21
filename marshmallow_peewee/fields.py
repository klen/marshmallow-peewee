from __future__ import annotations

from typing import Any, Optional, Union

import peewee as pw
from marshmallow import Schema, fields


class Related(fields.Nested):
    def __init__(
        self,
        nested: Optional[type[Schema]] = None,
        meta: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        self.field = None
        self.meta = meta or {}
        super(Related, self).__init__(nested, **kwargs)  # type: ignore[arg-type]

    def init_model(self, model: pw.Model, name: str):
        from .schema import ModelSchema

        field = model._meta.fields.get(name)  # type: ignore[]
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

    def _deserialize(self, value, attr, data, partial=None, **_):
        if self.field is None:
            raise RuntimeError("Init model first.")

        if not isinstance(value, dict):
            return self.field.rel_field.python_value(value)

        return super(Related, self)._deserialize(value, attr, data, partial=partial)


class ForeignKey(fields.Raw):
    string_keys = False

    def _bind_to_schema(self, field_name, schema):
        self.string_keys = schema.opts.string_keys
        super()._bind_to_schema(field_name, schema)

    def get_value(self, obj: pw.Model, attr, **_) -> Any:  # type: ignore[override]
        """Return the value for a given key from an object."""
        value = obj.__data__.get(self.metadata["name"])
        if value is not None and self.string_keys:
            return str(value)
        return value


class FKNested(fields.Nested):
    """Get an related instance from cache."""

    def __init__(self, nested: Union[type[Schema], type[pw.Model]], **kwargs):
        if issubclass(nested, pw.Model):
            nested = self.get_schema(nested, **kwargs)

        super(FKNested, self).__init__(nested, **kwargs)

    @staticmethod
    def get_schema(model_cls: type[pw.Model], **kwargs) -> type[Schema]:
        from .schema import ModelSchema

        class Schema(ModelSchema):
            class Meta:
                model = model_cls
                fields = kwargs.get("only", ())
                exclude = kwargs.get("exclude", ())

        return Schema

    def get_value(self, obj: pw.Model, attr: str, accessor=None, default=None):
        data_key = self.attribute or attr
        fk = obj.__data__.get(data_key)
        if fk is None:
            return None

        return obj.__rel__[data_key]
