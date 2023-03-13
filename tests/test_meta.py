from __future__ import annotations

from .models import User


def test_string_fields():
    from marshmallow_peewee import ModelSchema

    class BaseSchema(ModelSchema):
        class Meta:
            datetimeformat = "timestamp"

    class UserSchema(BaseSchema):
        class Meta:
            model = User
            string_keys = False

    user = User(id=1)
    data = UserSchema().dump(user)
    assert data
    assert data["id"] == 1
    assert isinstance(data["created"], float)
