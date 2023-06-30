from __future__ import annotations

from .models import Role, User


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

    role = Role(id=1)
    user = User(name="Mike", role=role, id=1)

    data = UserSchema().dump(user)
    assert "role_id" in data
    assert data["role_id"] == role.id  # type: ignore[]

    user2 = UserSchema().load(data)
    assert user2 == user
    assert user2.role_id == role.id  # type: ignore[]

    class BaseSchema2(BaseSchema[User]):
        class Meta:
            id_keys = True

    class UserSchema2(BaseSchema2):
        class Meta:
            model = User

    data = UserSchema2().dump(user)
    assert "role_id" in data
    assert data["role_id"] == str(role.id)  # type: ignore[]

    class UserSchema3(UserSchema2):
        pass

    data = UserSchema3().dump(user)
    assert "role_id" in data
    assert data["role_id"] == str(role.id)  # type: ignore[]
