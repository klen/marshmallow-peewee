import marshmallow as ma
import peewee as pw
from marshmallow.compat import with_metaclass

from .convert import ModelConverter, Related


class SchemaOpts(ma.SchemaOpts):

    def __init__(self, meta):
        super(SchemaOpts, self).__init__(meta)
        self.model = getattr(meta, 'model', None)
        self.dump_only_pk = getattr(meta, 'dump_only_pk', True)
        if self.model and not issubclass(self.model, pw.Model):
            raise ValueError("`model` must be a subclass of peewee.Model")
        self.model_converter = getattr(meta, 'model_converter', ModelConverter)


class SchemaMeta(ma.schema.SchemaMeta):

    @classmethod
    def get_declared_fields(mcs, klass, cls_fields, inherited_fields, dict_cls):
        declared_fields = dict_cls()
        opts = klass.opts
        base_fields = super(SchemaMeta, mcs).get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls
        )
        model = getattr(opts, 'model', None)
        if model:
            for name, field in base_fields.items():
                if isinstance(field, Related) and field.nested is None:
                    field.init_model(model, name)

            converter = opts.model_converter(opts=opts)
            declared_fields.update(converter.fields_for_model(model))
        declared_fields.update(base_fields)
        return declared_fields


class ModelSchema(with_metaclass(SchemaMeta, ma.Schema)):

    OPTIONS_CLASS = SchemaOpts

    def __init__(self, instance=None, **kwargs):
        self.instance = instance
        super(ModelSchema, self).__init__(**kwargs)

    @ma.post_load
    def make_instance(self, data):
        """Build object from data."""
        if not self.opts.model:
            return data

        if self.instance is not None:
            for key, value in data.items():
                setattr(self.instance, key, value)
            return self.instance

        return self.opts.model(**data)

    def load(self, data, instance=None, *args, **kwargs):
        self.instance = instance or self.instance
        return super(ModelSchema, self).load(data, *args, **kwargs)
