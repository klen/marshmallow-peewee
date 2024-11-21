from __future__ import annotations

from marshmallow_peewee import ModelSchema
from marshmallow_peewee.fields import FKNested
from marshmallow_peewee.types import TVModel

from .models import Role, User


def test_string_keys():
    class BaseSchema(ModelSchema):
        class Meta:
            datetimeformat = "timestamp"

    class UserSchema(BaseSchema):
        class Meta(BaseSchema.Meta):
            model = User
            string_keys = False

    user = User(id=1)
    data = UserSchema().dump(user)
    assert data
    assert data["id"] == 1
    assert isinstance(data["created"], float)


def test_fields():
    class UserSchema(ModelSchema):
        class Meta:
            model = User
            fields = "id", "name", "active"

    schema = UserSchema()
    assert schema.fields.keys() == {"id", "name", "active"}


def test_id_keys():
    class UserSchema(ModelSchema[User]):
        class Meta:
            model = User
            id_keys = True
            string_keys = False
            dump_only_pk = False

    role = Role(id=1)
    user = User(name="Mike", role=role, id=1)

    data = UserSchema().dump(user)
    assert "role_id" in data
    assert data["role_id"] == role.id  # type: ignore[]

    user2 = UserSchema().load(data)
    assert user2 == user
    assert user2.role_id == role.id  # type: ignore[]

    class BaseSchema2(ModelSchema[User]):
        class Meta:
            id_keys = True

    class UserSchema2(BaseSchema2):
        class Meta(BaseSchema2.Meta):
            model = User

    data = UserSchema2().dump(user)
    assert "role_id" in data
    assert data["role_id"] == str(role.id)  # type: ignore[]

    class UserSchema3(UserSchema2):
        pass

    data = UserSchema3().dump(user)
    assert "role_id" in data
    assert data["role_id"] == str(role.id)  # type: ignore[]


def test_id_keys_nested():
    class BaseSchema(ModelSchema[TVModel]):
        class Meta:
            id_keys = True

    class RoleSchema(BaseSchema[Role]):
        class Meta(BaseSchema.Meta):
            model = Role

    class UserSchema(BaseSchema[User]):
        role = FKNested(RoleSchema)

        class Meta(BaseSchema.Meta):
            model = User

    role = Role(id=1)
    user = User(name="Mike", role=role, id=1)

    data = UserSchema().dump(user)
    assert data["role_id"] == str(role.id)  # type: ignore[]
    assert data["role"]["id"] == str(role.id)  # type: ignore[]
