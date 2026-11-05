from collections.abc import Generator

import pytest

from tools.tasks import tasks


@pytest.fixture(autouse=True)
def setup_tasks() -> Generator[None]:
    tasks.clear()
    yield
    tasks.clear()