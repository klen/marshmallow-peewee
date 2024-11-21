from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Iterable,
    Literal,
    Mapping,
    Optional,
    Union,
    overload,
)

import marshmallow as ma
import peewee as pw
from marshmallow import schema

from .config import DEFAULTS
from .convert import DefaultConverter
from .fields import Related
from .types import TVModel


class SchemaOpts(ma.SchemaOpts, Generic[TVModel]):
    model: Optional[type[TVModel]]
    dump_only_pk: bool
    string_keys: bool
    id_keys: bool
    model_converter: type[DefaultConverter]

    def __init__(self, meta, **kwargs):
        super(SchemaOpts, self).__init__(meta, **kwargs)
        self.model = getattr(meta, "model", None)
        self.dump_only_pk = getattr(meta, "dump_only_pk", DEFAULTS["dump_only_pk"])
        self.string_keys = getattr(meta, "string_keys", DEFAULTS["string_keys"])
        self.id_keys = getattr(meta, "id_keys", DEFAULTS["id_keys"])

        if self.model and not issubclass(self.model, pw.Model):
            raise ValueError("`model` must be a subclass of peewee.Model")

        self.model_converter = getattr(meta, "model_converter", DefaultConverter)


INHERITANCE_OPTIONS = (
    "model",
    "model_converter",
    "dump_only_pk",
    "string_keys",
    "id_keys",
    # Basic options
    "datetimeformat",
    "dateformat",
    "timeformat",
    "unknown",
)


class SchemaMeta(schema.SchemaMeta):
    def __new__(cls, name, bases, attrs):
        """Support inheritance for model and model_converter Meta options."""
        if "Meta" in attrs and bases:
            meta = attrs["Meta"]
            base_meta = getattr(bases[0], "Meta", None)
            for option in INHERITANCE_OPTIONS:
                if hasattr(meta, option) or not hasattr(base_meta, option):
                    continue
                setattr(meta, option, getattr(base_meta, option))

        return super(SchemaMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def get_declared_fields(cls, klass, cls_fields, inherited_fields, dict_cls=dict):
        opts: SchemaOpts = klass.opts
        base_fields = super(SchemaMeta, cls).get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls
        )
        declared_fields = dict_cls()
        model = getattr(opts, "model", None)
        if model is not None:
            for name, field in base_fields.items():
                if isinstance(field, Related) and field.nested is None:
                    field.init_model(model, name)

            converter = opts.model_converter(opts=opts)
            declared_fields.update(converter.get_fields(model))
        declared_fields.update(base_fields)
        return declared_fields


class ModelSchema(ma.Schema, Generic[TVModel], metaclass=SchemaMeta):
    OPTIONS_CLASS = SchemaOpts

    opts: SchemaOpts[TVModel]
    Meta: ClassVar[type[Any]]

    def __init__(self, instance: Optional[TVModel] = None, **kwargs):
        self.instance = instance
        super(ModelSchema, self).__init__(**kwargs)

    @overload  # type: ignore[override]
    def load(
        self, data, *, many: Optional[Literal[False]] = None, **kwargs
    ) -> TVModel: ...

    @overload
    def load(
        self, data, *, many: Optional[Literal[True]] = None, **kwargs
    ) -> list[TVModel]: ...

    def load(
        self,
        data: Union[Mapping[str, Any], Iterable[Mapping[str, Any]]],
        *,
        instance: Optional[TVModel] = None,
        **kwargs,
    ):
        self.instance = instance or self.instance
        return super().load(data, **kwargs)

    @ma.post_load
    def make_instance(self, data: dict[str, Any], **params) -> Union[dict, TVModel]:
        """Build object from data."""
        if not self.opts.model:
            return data

        if self.instance is None:
            return self.opts.model(**data)

        for key, value in data.items():
            setattr(self.instance, key, value)

        return self.instance

    if TYPE_CHECKING:

        @overload  # type: ignore[override]
        def dump(self, obj) -> dict[str, Any]: ...

        @overload
        def dump(self, obj, *, many: Literal[False]) -> dict[str, Any]: ...

        @overload
        def dump(self, obj, *, many: Literal[True]) -> list[dict[str, Any]]: ...

        def dump(
            self, obj: Union[TVModel, Iterable[TVModel]], *, many: Optional[bool] = None
        ) -> Union[dict[str, Any], list[dict[str, Any]]]: ...
