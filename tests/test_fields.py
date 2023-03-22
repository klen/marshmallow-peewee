from __future__ import annotations

import pytest

from .models import Role, User, proxy


@pytest.fixture(autouse=True)
def _setup(db):
    proxy.initialize(db)
    db.create_tables([Role, User])


def test_related():
    from marshmallow_peewee import ModelSchema, Related

    class UserSchema(ModelSchema[User]):
        role = Related()

        class Meta:
            model = User
            string_keys = False

    role = Role.create(name="admin")
    user = User.create(name="Mike", role=role)

    data = UserSchema().dump(user)
    assert data
    assert data["role"]


def test_fknested():
    from marshmallow_peewee import FKNested, ModelSchema

    class UserSchema(ModelSchema[User]):
        role = FKNested(Role, only=("name",))

        class Meta:
            model = User
            string_keys = False

    role = Role.create(name="admin")
    user = User.create(name="Mike", role=role)

    data = UserSchema().dump(user)
    assert data
    assert data["role"]
    assert "id" not in data["role"]
