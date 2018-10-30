import datetime as dt

import peewee as pw


proxy = pw.Proxy()


class Role(pw.Model):
    name = pw.CharField(255, default='user')

    class Meta:
        database = proxy


class User(pw.Model):

    created = pw.DateTimeField(default=dt.datetime.now)
    name = pw.CharField(255)
    title = pw.CharField(127, null=True)
    active = pw.BooleanField(default=True)
    rating = pw.IntegerField(default=0)

    role = pw.ForeignKeyField(Role)

    class Meta:
        database = proxy
