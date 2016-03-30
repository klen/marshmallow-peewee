import peewee as pw
import datetime as dt


proxy = pw.Proxy()


class Role(pw.Model):
    name = pw.CharField(255, default='user')


class User(pw.Model):

    created = pw.DateTimeField(default=dt.datetime.now())
    name = pw.CharField(255)
    title = pw.CharField(127, null=True)
    active = pw.BooleanField(default=True)
    rating = pw.IntegerField(default=0)

    role = pw.ForeignKeyField(Role)

    class Meta:
        database = proxy


def test_base(db):
    assert db


def test_schema(db):
    proxy.initialize(db)
    db.create_tables([Role, User], safe=True)

    from marshmallow_peewee import ModelSchema

    class UserSchema(ModelSchema):
        class Meta:
            model = User

    role = Role.create()
    user = User.create(name='Mike', role=role)

    result, errors = UserSchema().dump(user)
    assert not errors
    assert result
    assert result['id'] == 1
    assert result['name'] == 'Mike'

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

    role = Role.create()
    user = User.create(name='Mike', role=role)

    result, errors = UserSchema().dump(user)
    assert not errors
    assert result
    assert result['role']['name'] == 'user'

    result, errors = UserSchema().load(result)
    assert not errors
    assert isinstance(result, User)
    assert result.id == 1
    assert isinstance(result.role, Role)

    result, errors = UserSchema().load({
        'name': 'Kevin',
        'role': '1'
    })
    assert not result.id
    assert result.role


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
