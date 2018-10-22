import peewee as pw
from marshmallow import fields, validate as ma_validate

from .compat import OrderedDict
from .fields import ForeignKey


class ModelConverter(object):

    """ Convert Peewee model to Marshmallow schema."""

    TYPE_MAPPING = {
        pw.AutoField: fields.String,
        pw.IntegerField: fields.Integer,
        pw.BigIntegerField: fields.Integer,
        pw.SmallIntegerField: fields.Integer,
        pw.FloatField: fields.Float,
        pw.DoubleField: fields.Float,
        pw.DecimalField: fields.Decimal,
        pw.CharField: fields.String,
        pw.FixedCharField: fields.String,
        pw.TextField: fields.String,
        pw.UUIDField: fields.UUID,
        pw.DateTimeField: fields.DateTime,
        pw.DateField: fields.Date,
        pw.TimeField: fields.Time,
        pw.BooleanField: fields.Boolean,
        pw.ForeignKeyField: ForeignKey,
    }
    try:
        TYPE_MAPPING[pw.BigAutoField] = fields.String
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
            'validate': field.python_value,
        }

        if field.default is not None:
            params['default'] = field.default

        # use first "known" field class from field class mro
        # so that extended field classes get converted correctly
        method = self.convert_default
        for klass in field.__class__.mro():
            try:
                method = getattr(self, 'convert_' + klass.__name__)
                break
            except AttributeError:
                if klass in self.TYPE_MAPPING:
                    break

        return method(field, **params)

    def convert_default(self, field, **params):
        """Return raw field."""
        ma_field = self.TYPE_MAPPING.get(type(field), fields.Raw)
        return ma_field(**params)

    def convert_AutoField(self, field, required=False, **params):
        return fields.String(dump_only=self.opts.dump_only_pk, required=False, **params)

    convert_BigAutoField = convert_AutoField

    def convert_CharField(self, field, validate=None, **params):
        validate = ma_validate.Length(max=field.max_length)
        return fields.String(validate=validate, **params)

    def convert_BooleanField(self, field, validate=None, **params):
        return fields.Boolean(**params)
