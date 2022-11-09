from datetime import datetime, timedelta, timezone, tzinfo

import pytest

from .models import Role, User, proxy


@pytest.fixture(autouse=True)
def setup(db):
    proxy.initialize(db)
    db.create_tables([Role, User])


def test_timestamp():
    from marshmallow_peewee import Timestamp

    user = User(name="Mike", created=datetime(2014, 1, 1, tzinfo=timezone.utc))

    ts = user.created.timestamp()

    field = Timestamp()
    test = field.serialize("created", user)
    assert test == user.created.timestamp() == ts

    test = field.deserialize(test)
    assert (
        test.replace(tzinfo=timezone.utc).timestamp() == user.created.timestamp() == ts
    )


def test_timestamp_with_tz():
    from marshmallow_peewee import Timestamp

    tz = timezone(timedelta(hours=3))
    user = User(name="Mike", created=datetime(2014, 1, 1, tzinfo=tz))

    field = Timestamp()
    test = field.serialize("created", user)
    assert test == user.created.timestamp()

    test = field.deserialize(test)
    assert test == user.created.astimezone(timezone.utc).replace(tzinfo=None)


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
