from datetime import datetime, timedelta, timezone, tzinfo

import pytest

from .models import Role, User, proxy


@pytest.fixture(autouse=True)
def setup(db):
    proxy.initialize(db)
    db.create_tables([Role, User])


def test_timestamp():
    from marshmallow_peewee import ModelSchema, Timestamp

    class UserSchema(ModelSchema):

        created = Timestamp()

        class Meta:
            model = User

    tz = timezone(timedelta(hours=3))
    user = User(name="Mike", created=datetime(2014, 1, 1, tzinfo=tz))

    schema = UserSchema()
    data = schema.dump(user)
    assert data["created"] == user.created.timestamp()


def test_related():
    from marshmallow_peewee import ModelSchema, Related

    class UserSchema(ModelSchema):
        role = Related()

        class Meta:
            model = User
            string_keys = False

    role = Role.create(name="admin")
    user = User.create(name="Mike", role=role)

    data = UserSchema().dump(user)
    assert data
    assert data["role"]
