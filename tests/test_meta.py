from __future__ import annotations

import pytest

from .models import Role, User, proxy


@pytest.fixture(autouse=True)
def _setup(db):
    proxy.initialize(db)
    db.create_tables([Role, User])


def test_string_keys():
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


def test_fields():
    from marshmallow_peewee import ModelSchema

    class UserSchema(ModelSchema):
        class Meta:
            model = User
            fields = "id", "name", "active"

    schema = UserSchema()
    assert schema.fields.keys() == {"id", "name", "active"}


def test_id_keys():
    from marshmallow_peewee import ModelSchema as BaseSchema

    class UserSchema(BaseSchema[User]):
        class Meta:
            model = User
            id_keys = True
            string_keys = False
            dump_only_pk = False

    role = Role.create()
    user = User.create(name="Mike", role=role)

    data = UserSchema().dump(user)
    assert "role_id" in data
    assert data["role_id"] == role.id

    user2 = UserSchema().load(data)
    assert user2 == user
    assert user2.role == role

    class BaseSchema2(BaseSchema[User]):
        class Meta:
            id_keys = True

    class UserSchema2(BaseSchema2):
        class Meta:
            model = User

    data = UserSchema2().dump(user)
    assert "role_id" in data
    assert data["role_id"] == str(role.id)
