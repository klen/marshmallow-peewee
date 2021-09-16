Marshmallow-Peewee
##################


.. _badges:

.. image:: http://img.shields.io/travis/klen/marshmallow-peewee.svg?style=flat-square
    :target: http://travis-ci.org/klen/marshmallow-peewee
    :alt: Build Status

.. image:: http://img.shields.io/pypi/v/marshmallow-peewee.svg?style=flat-square
    :target: https://pypi.python.org/pypi/marshmallow-peewee
    :alt: Version

.. image:: http://img.shields.io/pypi/l/marshmallow-peewee.svg?style=flat-square
    :target: https://pypi.python.org/pypi/marshmallow-peewee
    :alt: License

.. _description:

Marshmallow-Peewee -- Peewee_ integration with the Marshmallow_ (de)serialization library.

Dependency Note
---------------

For ``Marshmallow<3``/``Python<3`` please use ``Marshmallow-Peewee<3``.

.. code-block:: python

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

    result, errors = UserSchema().dump(user)
    print(result)
    # {'active': True,
    #  'created': '2016-03-29T15:27:18.600034+00:00',
    #  'id': 1,
    #  'name': 'Mike',
    #  'rating': 0,
    #  'role': 1,
    #  'title': None}

    result, errors = UserSchema().load(result)
    assert isinstance(result, User)
    assert result.name == 'Mike'

    from marshmallow_peewee import Related

    class UserSchema(ModelSchema):

        role = Related()

        class Meta:
            model = User

    result, errors = UserSchema().dump(user)
    print(result)
    # {'active': True,
    #  'created': '2016-03-29T15:30:32.767483+00:00',
    #  'id': 1,
    #  'name': 'Mike',
    #  'rating': 0,
    #  'role': {'id': 5, 'name': 'user'},
    #  'title': None}

    result, errors = UserSchema().load(result)
    assert not errors
    assert isinstance(result, User)
    assert isinstance(result.role, Role)

.. _contents:

.. contents::

Requirements
=============

- python 3.7+

.. _installation:

Installation
=============

**Marshmallow-Peewee** should be installed using pip: ::

    pip install Marshmallow-Peewee

.. note::

    Marshmallow-Peewee>=2.0.0 supports only Peewee>=3.0.0. For Peewee<3.0.0
    please use Marhmallow-Peewee==1.2.7

.. _usage:

Usage
=====

.. code-block:: python

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
            # model_converter = marshmallow_peewee.ModelConverter

            # dump_only_pk: Primary key is dump only
            # dump_only_pk = True

            # string_keys: Convert keys to strings
            # string_keys = True


.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/marshmallow-peewee/issues

.. _contributing:

Contributing
============

Development of The Marshmallow-Peewee happens at: https://github.com/klen/marshmallow-peewee

.. _license:

License
========

Licensed under a MIT license (See LICENSE)

.. _links:

.. _klen: https://github.com/klen
.. _Peewee: http://docs.peewee-orm.com/en/latest/
.. _Marshmallow: https://marshmallow.readthedocs.org/en/latest/
