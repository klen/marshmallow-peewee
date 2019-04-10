from collections import OrderedDict

import peewee as pw
from marshmallow import ValidationError, compat, fields
from marshmallow import validate as ma_validate

from .fields import ForeignKey


class ModelConverter(object):

    """ Convert Peewee model to Marshmallow schema."""

    TYPE_MAPPING = [
        (pw.AutoField, fields.String),
        (pw.IntegerField, fields.Integer),
        (pw.CharField, fields.String),
        (pw.BooleanField, fields.Boolean),
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
    ]

    try:
        TYPE_MAPPING.append((pw.BigAutoField, fields.String))
    except AttributeError:
        pass

    def __init__(self, opts):
        self.opts = opts

    def fields_for_model(self, model):
        result = OrderedDict()
        for field in model._meta.sorted_fields:
            ma_field = self.convert_field(field)
            if ma_field:
                result[field.name] = ma_field
        return result

    def convert_field(self, field):
        params = {
            'allow_none': field.null,
            'attribute': field.name,
            'required': not field.null and field.default is None,
            'validate': [convert_value_validate(field.db_value)],
        }

        if field.default is not None:
            params['default'] = field.default

        if field.choices is not None:
            choices = []
            labels = []
            for c in field.choices:
                choices.append(c[0])
                labels.append(c[1])
            params['validate'].append(ma_validate.OneOf(choices, labels))

        # use first "known" field class from field class mro
        # so that extended field classes get converted correctly
        for klass in field.__class__.mro():
            method = getattr(self, 'convert_' + klass.__name__, None)
            if method or klass in self.TYPE_MAPPING:
                break

        method = method or self.convert_default
        return method(field, **params)

    def convert_default(self, field, **params):
        """Return raw field."""
        for klass, ma_field in self.TYPE_MAPPING:
            if isinstance(field, klass):
                return ma_field(**params)
        return fields.Raw(**params)

    def convert_AutoField(self, field, required=False, **params):
        ftype = fields.String if self.opts.string_keys else fields.Integer
        return ftype(dump_only=self.opts.dump_only_pk, required=False, **params)

    convert_BigAutoField = convert_AutoField

    def convert_CharField(self, field, validate=None, **params):
        validate += [ma_validate.Length(max=field.max_length)]
        return fields.String(validate=validate, **params)

    def convert_BooleanField(self, field, validate=None, **params):
        return fields.Boolean(**params)


def convert_value_validate(converter):
    def validator(value):
        try:
            converter(value)
        except Exception as e:
            raise ValidationError(compat.text_type(e))

    return validator
