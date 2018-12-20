import pytest
import peewee as pw
import datetime as dt
import marshmallow as ma

from .models import proxy, Role, User


if ma.__version__.split('.') >= ['3']:
    pytest.skip('Skip tests for Marshmallow 2', allow_module_level=True)


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
    result, errors = schema.load({'name': 'Bob', 'role': 1, 'active': False})
    assert not errors
    assert result.role
    assert not result.active

    result, errors = UserSchema().dump(user)
    assert not errors
    assert result
    assert result['id'] == 1
    assert result['name'] == 'Mike'
    assert result['role'] == role.id
    assert result['created'] > 100000

    result, errors = UserSchema().load(result)
    assert not errors
    assert isinstance(result, User)
    assert result.name == 'Mike'


def test_schema_related(db):
    proxy.initialize(db)
    db.create_tables([Role, User], safe=True)

    from marshmallow_peewee import ModelSchema, Related

    class UserSchema(ModelSchema):

        role = Related()

        class Meta:
            model = User
            dump_only_pk = False
            exclude = 'rating',

    role = Role.create()
    user = User.create(name='Mike', role=role)

    assert UserSchema._declared_fields['role'].attribute == 'role'

    result, errors = UserSchema().dump(user)
    assert not errors
    assert result
    assert result['role']['name'] == 'user'
    assert 'rating' not in result

    result, errors = UserSchema().load(result)
    assert not errors
    assert isinstance(result, User)
    assert result.id == 1
    assert isinstance(result.role, Role)

    result, errors = UserSchema().load({
        'name': 'Kevin',
        'role': 1
    })
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

    result, errors = UserSchema().dump(user)
    assert not errors
    assert result
    assert 'name' not in result['role']

    class RoleSchema(ModelSchema):

        user_set = Related()

        class Meta:
            model = Role

    result, errors = RoleSchema().dump(user.role)
    assert result
    assert result['user_set']
    assert not errors


def tests_partition(db):
    proxy.initialize(db)
    db.create_tables([Role, User], safe=True)

    from marshmallow_peewee import ModelSchema

    class UserSchema(ModelSchema):
        class Meta:
            model = User

    role = Role.create()
    user = User.create(name='Mike', role=role)

    result, errors = UserSchema().load({
        'name': 'David'
    }, instance=user, partial=True)
    assert result.id == user.id
    assert user.name == 'David'


def test_custom_converter(db):
    from marshmallow_peewee import ModelSchema, Related
    from marshmallow_peewee.convert import ModelConverter

    class CustomModelConverter(ModelConverter):

        def convert_BooleanField(self, field, **params):
            return ma.fields.Int(**params)

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
    serialized = UserSchema().dump(user).data
    assert serialized['active'] is 1
