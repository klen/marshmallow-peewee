import marshmallow as ma
import pytest

from .models import User


@pytest.fixture
def convertor():
    from marshmallow_peewee.convert import ModelConverter
    from marshmallow_peewee.schema import SchemaOpts

    class Meta:
        model = User

    return ModelConverter(SchemaOpts(Meta))


def test_boolean(convertor):
    ma_field = convertor.convert_field(User.active)
    assert ma_field
    assert isinstance(ma_field, ma.fields.Boolean)
    assert ma_field.load_default is True
    assert ma_field.metadata
    assert ma_field.metadata["help_text"] == "Is user active"
