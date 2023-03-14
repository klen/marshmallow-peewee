from __future__ import annotations

import datetime as dt

import marshmallow as ma
import peewee as pw


class User(pw.Model):
    created = pw.DateTimeField(default=dt.datetime.now)
    title = pw.CharField(127, null=True)
    active = pw.BooleanField(default=True, help_text="Is user active")
    rating = pw.BigIntegerField(default=0)


def test_schema():

    from marshmallow_peewee import ModelSchema

    class UserSchema(ModelSchema):
        class Meta:
            model = User
            unknown = ma.EXCLUDE

    user = User(title="foo", active=True, rating=42)
    schema = UserSchema()
    data = schema.dump(user)
    assert data == {
        "id": None,
        "created": user.created.isoformat(),
        "title": "foo",
        "active": True,
        "rating": 42,
    }

    user = schema.load(data)
    assert user.title == "foo"
    assert user.active is True
    assert user.rating == 42
