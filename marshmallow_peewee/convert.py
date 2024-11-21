from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Optional, cast, overload

import peewee as pw
from marshmallow import ValidationError, fields
from marshmallow import validate as ma_validate

from .fields import ForeignKey

if TYPE_CHECKING:
    from collections.abc import Callable

    from .schema import SchemaOpts
    from .types import TFieldMappingList


class ModelConverterMeta(type):
    """Metaclass for ModelConverter."""

    def __new__(cls, name, bases, attrs):
        kls = super().__new__(cls, name, bases, attrs)
        kls.TYPE_MAPPING = list(kls.TYPE_MAPPING)  # type: ignore[attr-defined]
        return kls


class DefaultConverter(metaclass=ModelConverterMeta):
    """Convert Peewee model to Marshmallow schema."""

    TYPE_MAPPING: TFieldMappingList = []

    def __init__(self, opts: SchemaOpts):
        self.opts = opts

    def get_fields(self, model: pw.Model) -> OrderedDict[str, fields.Field]:
        result = OrderedDict()
        meta = cast(pw.Metadata, model._meta)  # type: ignore[]
        id_keys = self.opts.id_keys
        for field in meta.sorted_fields:
            data_key = field.name
            if id_keys and isinstance(
                field, (pw.ForeignKeyField, pw.DeferredForeignKey)
            ):
                data_key = field.column_name

            ma_field = self.convert(field, data_key)
            if not ma_field:
                continue

            result[data_key] = ma_field

        return result

    @overload
    @classmethod
    def register(cls, field: type[pw.Field]) -> Callable[[Callable], Callable]: ...

    @overload
    @classmethod
    def register(cls, field: type[pw.Field], ma_field: type[fields.Field]) -> None: ...

    @classmethod
    def register(
        cls,
        field: type[pw.Field],
        ma_field: Optional[type[fields.Field]] = None,
    ) -> Callable[[Callable], Callable] | None:
        if ma_field is None:

            def wrapper(fn):
                cls.TYPE_MAPPING.insert(0, (field, fn))
                return fn

            return wrapper

        builder = generate_builder(ma_field)
        cls.register(field)(builder)

        return None

    def convert(self, field: pw.Field, data_key: Optional[str] = None) -> fields.Field:
        params = {
            "data_key": data_key or field.name,
            "allow_none": field.null,
            "required": not field.null and field.default is None,
            "validate": [convert_value_validate(field.db_value)],
        }

        if field.null:
            params["load_default"] = None

        if field.default is not None:
            params["load_default"] = field.default

        if field.choices is not None:
            choices = []
            labels = []
            for c in field.choices:
                choices.append(c[0])
                labels.append(c[1])
            params["validate"].append(ma_validate.OneOf(choices, labels))

        params["metadata"] = {"name": field.name}
        if field.help_text:
            params["metadata"]["description"] = field.help_text

        # use first "known" field class from field class mro
        # so that extended field classes get converted correctly
        for cls in field.__class__.__mro__:
            for pw_field, builder in self.TYPE_MAPPING:
                if cls is pw_field:
                    return builder(field, self.opts, **params)

        return DEFAULT_BUILDER(field, self.opts, **params)


def generate_builder(ma_field_cls: type[fields.Field]) -> Callable:
    """Generate builder function for given marshmallow field."""

    def builder(_: pw.Field, __: SchemaOpts, **params) -> fields.Field:
        return ma_field_cls(**params)

    return builder


DEFAULT_BUILDER = generate_builder(fields.Raw)


DefaultConverter.register(pw.IntegerField, ma_field=fields.Integer)
DefaultConverter.register(pw.DateTimeField, ma_field=fields.DateTime)
DefaultConverter.register(pw.DateField, ma_field=fields.Date)
DefaultConverter.register(pw.TextField, ma_field=fields.String)
DefaultConverter.register(pw.ForeignKeyField, ma_field=ForeignKey)
DefaultConverter.register(pw.DeferredForeignKey, ma_field=ForeignKey)
DefaultConverter.register(pw.FloatField, ma_field=fields.Float)
DefaultConverter.register(pw.DecimalField, ma_field=fields.Decimal)
DefaultConverter.register(pw.TimeField, ma_field=fields.Time)
DefaultConverter.register(pw.BigIntegerField, ma_field=fields.Integer)
DefaultConverter.register(pw.SmallIntegerField, ma_field=fields.Integer)
DefaultConverter.register(pw.DoubleField, ma_field=fields.Float)
DefaultConverter.register(pw.FixedCharField, ma_field=fields.String)
DefaultConverter.register(pw.UUIDField, ma_field=fields.UUID)


@DefaultConverter.register(pw.AutoField)  # type: ignore[]
def convert_autofield(_: pw.Field, opts: SchemaOpts, **params) -> fields.Field:
    ftype = fields.String if opts.string_keys else fields.Integer
    params["required"] = False
    return ftype(dump_only=opts.dump_only_pk, **params)


@DefaultConverter.register(pw.CharField)  # type: ignore[]
def convert_charfield(
    field: pw.CharField,
    _: SchemaOpts,
    *,
    validate: Optional[list] = None,
    **params,
) -> fields.Field:
    if validate is None:
        validate = []

    validate += [ma_validate.Length(max=field.max_length)]
    return fields.String(validate=validate, **params)


@DefaultConverter.register(pw.BooleanField)  # type: ignore[]
def convert_booleanfield(
    _: pw.BooleanField,
    __: SchemaOpts,
    **params,
) -> fields.Field:
    return fields.Boolean(**params)


def convert_value_validate(converter: Callable) -> Callable:
    def validator(value):
        try:
            converter(value)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(str(exc)) from exc

    return validator


# ruff: noqa: N802, N815, ARG002
