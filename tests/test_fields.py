from datetime import datetime, timedelta, timezone, tzinfo

from .models import User


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
