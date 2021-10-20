import pytest
import marshmallow as ma

from .models import User


@pytest.fixture
def convertor():
    from marshmallow_peewee.schema import SchemaOpts
    from marshmallow_peewee.convert import ModelConverter

    class Meta:
        model = User

    return ModelConverter(SchemaOpts(Meta))


def test_boolean(convertor):
    ma_field = convertor.convert_field(User.active)
    assert ma_field
    assert isinstance(ma_field, ma.fields.Boolean)
    assert ma_field.load_default is True
