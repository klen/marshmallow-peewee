from __future__ import annotations

import pytest

from .models import Role, User, proxy


@pytest.fixture(autouse=True)
def _setup(db):
    proxy.initialize(db)
    db.create_tables([Role, User])


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
