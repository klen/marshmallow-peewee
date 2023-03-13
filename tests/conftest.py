from __future__ import annotations

import pytest


@pytest.fixture()
def db():
    from playhouse.db_url import connect

    database = connect("sqlite:///:memory:")
    yield database
    if not database.is_closed():
        database.close()
