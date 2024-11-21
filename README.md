# Marshmallow-Peewee

Marshmallow-Peewee -- [Peewee ORM](https://github.com/coleifer/peewee)
integration with the
[Marshmallow](https://github.com/marshmallow-code/marshmallow)
(de)serialization library.

[![Tests Status](https://github.com/klen/marshmallow-peewee/workflows/tests/badge.svg)](https://github.com/klen/marshmallow-peewee/actions)
[![PYPI Version](https://img.shields.io/pypi/v/marshmallow-peewee)](https://pypi.org/project/marshmallow-peewee/)
[![Python Versions](https://img.shields.io/pypi/pyversions/marshmallow-peewee)](https://pypi.org/project/marshmallow-peewee/)


## Requirements

* python >= 3.9

## Installation

**marshmallow-peewee** should be installed using pip:

```shell
$ pip install marshmallow-peewee
```

### Quickstart

```python
    import peewee as pw


    class Role(pw.Model):
        name = pw.CharField(255, default='user')


    class User(pw.Model):

        created = pw.DateTimeField(default=dt.datetime.now())
        name = pw.CharField(255)
        title = pw.CharField(127, null=True)
        active = pw.BooleanField(default=True)
        rating = pw.IntegerField(default=0)

        role = pw.ForeignKeyField(Role)


    from marshmallow_peewee import ModelSchema

    class UserSchema(ModelSchema):

        class Meta:
            model = User

    role = Role.create()
    user = User.create(name='Mike', role=role)

    result = UserSchema().dump(user)
    print(result)
    # {'active': True,
    #  'created': '2016-03-29T15:27:18.600034+00:00',
    #  'id': 1,
    #  'name': 'Mike',
    #  'rating': 0,
    #  'role': 1,
    #  'title': None}

    result = UserSchema().load(result)
    assert isinstance(result, User)
    assert result.name == 'Mike'

    from marshmallow_peewee import Related

    class UserSchema(ModelSchema):

        role = Related()

        class Meta:
            model = User

    result = UserSchema().dump(user)
    print(result)
    # {'active': True,
    #  'created': '2016-03-29T15:30:32.767483+00:00',
    #  'id': 1,
    #  'name': 'Mike',
    #  'rating': 0,
    #  'role': {'id': 5, 'name': 'user'},
    #  'title': None}

    result = UserSchema().load(result)
    assert isinstance(result, User)
    assert isinstance(result.role, Role)
```

## Usage

```python

    import peewee as pw


    class Role(pw.Model):
        name = pw.CharField(255, default='user')


    class User(pw.Model):

        created = pw.DateTimeField(default=dt.datetime.now())
        name = pw.CharField(255)
        title = pw.CharField(127, null=True)
        active = pw.BooleanField(default=True)
        rating = pw.IntegerField(default=0)

        role = pw.ForeignKeyField(Role)


    from marshmallow_peewee import ModelSchema

    class UserSchema(ModelSchema):

        class Meta:

            # model: Bind peewee.Model to the Schema
            model = User

            # model_converter: Use custom model_converter
            # model_converter = marshmallow_peewee.DefaultConverter

            # dump_only_pk: Primary key is dump only
            # dump_only_pk = True

            # string_keys: Convert keys to strings
            # string_keys = True

            # id_keys: serialize (and deserialize) ForeignKey fields with _id suffix
            # id_keys = False
```

You may set global options for `marshmallow-peewee`:

```python

from marshmallow_peewee import setup

setup(id_keys=True, string_keys=False)  # Set options for all schemas

class UserSchema(ModelSchema):
  # ...

```

Customize fields convertion:

```python

from marshmallow_peewee import DefaultConverter

# Customize global

# Serialize boolean as string
DefaultConverter.register(peewee.BooleanField, marshmallow.fields.String)

# Alternative method
@DefaultConverter.register(peewee.BooleanField)
def build_field(field: peewee.Field, opts, **field_params):
  return marshmallow.fields.String(**params)

# Customize only for a scheme

class CustomConverter(DefaultConverter):
  pass


CustomConverter.register(...)


class CustomSchema(ModelSchema): # may be inherited
  class Meta:
    model_converter = CustomConverter


````

## Bug tracker

If you have any suggestions, bug reports or annoyances please report them to
the issue tracker at https://github.com/klen/marshmallow-peewee/issues


## Contributing

Development of the project happens at: https://github.com/klen/marshmallow-peewee


## License

Licensed under a [MIT License](http://opensource.org/licenses/MIT)
