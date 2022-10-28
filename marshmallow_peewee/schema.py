from typing import Any, Dict, Iterable, Mapping, Optional, Type, Union

import marshmallow as ma
import peewee as pw

from . import DEFAULTS
from .convert import ModelConverter
from .fields import Related


class SchemaOpts(ma.SchemaOpts):

    model: Optional[Type[pw.Model]]
    dump_only_pk: bool
    string_keys: bool
    id_keys: bool

    def __init__(self, meta, **kwargs):
        super(SchemaOpts, self).__init__(meta, **kwargs)
        self.model = getattr(meta, "model", None)
        self.dump_only_pk = getattr(meta, "dump_only_pk", DEFAULTS["dump_only_pk"])
        self.string_keys = getattr(meta, "string_keys", DEFAULTS["string_keys"])
        self.id_keys = getattr(meta, "id_keys", DEFAULTS["id_keys"])

        if self.model and not issubclass(self.model, pw.Model):
            raise ValueError("`model` must be a subclass of peewee.Model")

        self.model_converter = getattr(meta, "model_converter", ModelConverter)


INHERITANCE_OPTIONS = "model", "model_converter", "dump_only_pk", "string_keys"


class SchemaMeta(ma.schema.SchemaMeta):
    def __new__(mcs, name, bases, attrs):
        """Support inheritance for model and model_converter Meta options."""
        if "Meta" in attrs and bases:
            meta = attrs["Meta"]
            base_meta = getattr(bases[0], "Meta", None)
            for option in INHERITANCE_OPTIONS:
                if hasattr(meta, option) or not hasattr(base_meta, option):
                    continue
                setattr(meta, option, getattr(base_meta, option))

        return super(SchemaMeta, mcs).__new__(mcs, name, bases, attrs)

    @classmethod
    def get_declared_fields(mcs, klass, cls_fields, inherited_fields, dict_cls):
        declared_fields = dict_cls()
        opts = klass.opts
        base_fields = super(SchemaMeta, mcs).get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls
        )
        model = getattr(opts, "model", None)
        if model:
            for name, field in base_fields.items():
                if isinstance(field, Related) and field.nested is None:
                    field.init_model(model, name)

            converter = opts.model_converter(opts=opts)
            declared_fields.update(converter.fields_for_model(model))
        declared_fields.update(base_fields)
        return declared_fields


class ModelSchema(ma.Schema, metaclass=SchemaMeta):

    OPTIONS_CLASS = SchemaOpts

    opts: SchemaOpts

    def __init__(self, instance: pw.Model = None, **kwargs):
        self.instance = instance
        super(ModelSchema, self).__init__(**kwargs)

    @ma.post_load
    def make_instance(self, data: Dict, **_) -> Union[Dict, pw.Model]:
        """Build object from data."""
        if not self.opts.model:
            return data

        if self.instance is not None:
            for key, value in data.items():
                setattr(self.instance, key, value)
            return self.instance

        return self.opts.model(**data)

    def load(
        self,
        data: Union[Mapping[str, Any], Iterable[Mapping[str, Any]]],
        instance: pw.Model = None,
        *args,
        **kwargs
    ):
        self.instance = instance or self.instance
        return super(ModelSchema, self).load(data, *args, **kwargs)
