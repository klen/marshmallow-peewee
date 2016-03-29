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
            raise ValueError("`model` must be a subclass of mongoengine.base.BaseDocument")
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
                if isinstance(field, Related):
                    field.init_model(model, name)

            converter = opts.model_converter(opts=opts)
            declared_fields.update(converter.fields_for_model(model))
        declared_fields.update(base_fields)
        return declared_fields


class ModelSchema(with_metaclass(SchemaMeta, ma.Schema)):

    OPTIONS_CLASS = SchemaOpts

    @ma.post_load
    def _make_object(self, data):
        """Build object from data."""
        if self.opts.model:
            return self.opts.model(**data)
        return data
