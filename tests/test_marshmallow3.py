import pytest
import json
import peewee as pw
import datetime as dt
import marshmallow as ma

from .models import proxy, Role, User


def test_schema(db):
    proxy.initialize(db)
    db.create_tables([Role, User])

    from marshmallow_peewee import ModelSchema, MSTimestamp

    class UserSchema(ModelSchema):

        created = MSTimestamp()

        class Meta:
            model = User

    role = Role.create()
    user = User.create(name='Mike', role=role)

    schema = UserSchema()
    result = schema.load({'name': 'Bob', 'role': 1, 'active': False})
    assert result.role
    assert not result.active

    result = UserSchema().dump(user)
    assert result
    assert result['id'] == '1'
    assert result['name'] == 'Mike'
    assert result['role'] == str(role.id)
    assert result['created'] > 100000

    result = UserSchema().load(result, unknown=ma.EXCLUDE)
    assert isinstance(result, User)
    assert result.name == 'Mike'

    class ModelSchema_(ModelSchema):

        class Meta:
            string_keys = False

    class UserSchema(ModelSchema_):

        created = MSTimestamp()

        class Meta:
            model = User

    result = UserSchema().dump(user)
    assert result
    assert result['id'] == 1


def test_schema_related(db):
    proxy.initialize(db)
    db.create_tables([Role, User], safe=True)

    from marshmallow_peewee import ModelSchema, Related

    class UserSchema(ModelSchema):

        role = Related(unknown=ma.EXCLUDE)

        class Meta:
            model = User
            dump_only_pk = False
            exclude = 'rating',

    role = Role.create()
    user = User.create(name='Mike', role=role)

    assert UserSchema._declared_fields['role'].attribute == 'role'

    result = UserSchema().dump(user)
    assert result
    assert result['role']['name'] == 'user'
    assert 'rating' not in result

    result = UserSchema().load(result, unknown=ma.EXCLUDE)
    assert isinstance(result, User)
    assert result.id == '1'
    assert isinstance(result.role, Role)

    result = UserSchema().load({
        'name': 'Kevin',
        'role': u'1'
    }, unknown=ma.EXCLUDE)
    assert not result.id
    assert result.role

    class RoleSchema(ModelSchema):

        class Meta:
            model = Role
            fields = 'id',

    class UserSchema(ModelSchema):

        role = Related(RoleSchema)

        class Meta:
            model = User
            dump_only_pk = False

    result = UserSchema().dump(user)
    assert result
    assert 'name' not in result['role']

    class RoleSchema(ModelSchema):

        user_set = Related()

        class Meta:
            model = Role

    result = RoleSchema().dump(user.role)
    assert result
    assert result['user_set']


def tests_partition(db):
    proxy.initialize(db)
    db.create_tables([Role, User], safe=True)

    from marshmallow_peewee import ModelSchema

    class UserSchema(ModelSchema):
        class Meta:
            model = User

    role = Role.create()
    user = User.create(name='Mike', role=role)

    result = UserSchema().load({
        'name': 'David'
    }, instance=user, partial=True)
    assert result.id == user.id
    assert user.name == 'David'


def test_custom_converter(db):
    from marshmallow_peewee import ModelSchema, Related
    from marshmallow_peewee.convert import ModelConverter

    class CustomModelConverter(ModelConverter):

        def convert_BooleanField(self, field, **params):
            return ma.fields.String(**params)

    proxy.initialize(db)
    db.create_tables([Role, User], safe=True)

    class CustomModelSchema(ModelSchema):

        class Meta:
            model_converter = CustomModelConverter

    class UserSchema(CustomModelSchema):

        class Meta:
            model = User

    assert UserSchema.opts.model_converter is CustomModelConverter

    role = Role.create()
    user = User.create(name='Mike', role=role)
    serialized = UserSchema().dump(user)
    assert serialized['active'] == 'True'


@pytest.mark.parametrize('created_val', [
    '',
    'i_am_not_a_number',
])
def test_field_error(db, created_val):
    proxy.initialize(db)
    db.create_tables([Role, User])

    from marshmallow_peewee import ModelSchema, Timestamp

    class UserSchema(ModelSchema):

        created = Timestamp()

        class Meta:
            model = User

    Role.create()

    payload = {
        "name": "Denis",
        "role": "1",
    }

    payload['created'] = created_val

    with pytest.raises(ma.exceptions.ValidationError):
        UserSchema().loads(json.dumps(payload))
