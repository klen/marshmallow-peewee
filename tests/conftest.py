from __future__ import annotations

import pytest
from playhouse.db_url import connect


@pytest.fixture
def db():
    database = connect("sqlite:///:memory:")
    yield database
    if not database.is_closed():
        database.close()
