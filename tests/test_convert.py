from __future__ import annotations

from typing import TYPE_CHECKING

import marshmallow as ma
import peewee as pw
import pytest
from marshmallow_peewee.fields import ForeignKey

from .models import User

if TYPE_CHECKING:
    from marshmallow_peewee.convert import DefaultConverter


@pytest.fixture()
def converter():
    from marshmallow_peewee.convert import DefaultConverter
    from marshmallow_peewee.schema import SchemaOpts

    class CustomConverter(DefaultConverter):
        pass

    class Meta:
        model = User

    return CustomConverter(SchemaOpts(Meta))


def test_boolean(converter: DefaultConverter):
    ma_field = converter.convert(User.active)
    assert ma_field
    assert isinstance(ma_field, ma.fields.Boolean)
    assert ma_field.load_default is True
    assert ma_field.metadata
    assert ma_field.metadata["description"] == "Is user active"


def test_deferred(converter: DefaultConverter):
    class Test(pw.Model):
        user = pw.DeferredForeignKey("Child")

    ma_field = converter.convert(Test.user)
    assert isinstance(ma_field, ForeignKey)


def test_register(converter: DefaultConverter):
    converter.register(pw.BooleanField, ma.fields.String)
    ma_field = converter.convert(User.active)
    assert ma_field
    assert isinstance(ma_field, ma.fields.String)

    @converter.register(pw.BooleanField)
    def convert_boolean(field, opts, **params):
        return ma.fields.String(load_default="yes")

    ma_field = converter.convert(User.active)
    assert ma_field
    assert isinstance(ma_field, ma.fields.String)
    assert ma_field.load_default == "yes"
