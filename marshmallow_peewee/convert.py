from __future__ import annotations

import typing as t
from collections import OrderedDict

import peewee as pw
from marshmallow import ValidationError, fields
from marshmallow import validate as ma_validate

from .fields import ForeignKey


class ModelConverter:
    """Convert Peewee model to Marshmallow schema."""

    TYPE_MAPPING = [
        (pw.IntegerField, fields.Integer),
        (pw.DateTimeField, fields.DateTime),
        (pw.DateField, fields.Date),
        (pw.TextField, fields.String),
        (pw.ForeignKeyField, ForeignKey),
        (pw.FloatField, fields.Float),
        (pw.DecimalField, fields.Decimal),
        (pw.TimeField, fields.Time),
        (pw.BigIntegerField, fields.Integer),
        (pw.SmallIntegerField, fields.Integer),
        (pw.DoubleField, fields.Float),
        (pw.FixedCharField, fields.String),
        (pw.UUIDField, fields.UUID),
        # Overrided
        #  (pw.AutoField, fields.String),
        #  (pw.BigAutoField, fields.String),
        #  (pw.CharField, fields.String),
        #  (pw.BooleanField, fields.Boolean),
    ]

    def __init__(self, opts: SchemaOpts):
        self.opts = opts

    def fields_for_model(self, model: pw.Model) -> OrderedDict:
        result = OrderedDict()
        for field in model._meta.sorted_fields:
            name = field.name
            if self.opts.id_keys and isinstance(field, pw.ForeignKeyField):
                name = field.column_name

            ma_field = self.convert_field(field)
            if ma_field:
                result[name] = ma_field

        return result

    def convert_field(self, field: pw.Field) -> fields.Field:
        params = {
            "allow_none": field.null,
            "attribute": field.name,
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

        # use first "known" field class from field class mro
        # so that extended field classes get converted correctly
        method = None
        for klass in field.__class__.mro():
            method = getattr(self, "convert_" + klass.__name__, None)
            if method:
                break

        method = method or self.convert_default
        return method(field, **params)

    def convert_default(self, field: pw.Field, **params) -> fields.Field:
        """Return raw field."""
        for klass, ma_field in self.TYPE_MAPPING:
            if isinstance(field, klass):
                return ma_field(**params)
        return fields.Raw(**params)

    def convert_AutoField(
        self, field: pw.Field, required: bool = False, **params
    ) -> fields.Field:
        ftype = fields.String if self.opts.string_keys else fields.Integer
        return ftype(dump_only=self.opts.dump_only_pk, required=False, **params)

    convert_BigAutoField = convert_AutoField

    def convert_CharField(
        self, field: pw.CharField, validate: t.List = None, **params
    ) -> fields.Field:
        if validate is None:
            validate = []

        validate += [ma_validate.Length(max=field.max_length)]
        return fields.String(validate=validate, **params)

    def convert_BooleanField(
        self, field: pw.Field, validate: t.List = None, **params
    ) -> fields.Field:
        return fields.Boolean(**params)


def convert_value_validate(converter: t.Callable) -> t.Callable:
    def validator(value):
        try:
            converter(value)
        except Exception as e:
            raise ValidationError(str(e))

    return validator


if t.TYPE_CHECKING:
    from .schema import SchemaOpts
