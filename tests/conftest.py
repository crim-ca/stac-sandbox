import asyncio
import json
import os
import time
from typing import Callable, Dict

import pytest
from httpx import AsyncClient

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def app_client(app):
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture
def load_test_data() -> Callable[[str], Dict]:
    def load_file(filename: str) -> Dict:
        with open(os.path.join(DATA_DIR, filename)) as file:
            return json.load(file)

    return load_file
