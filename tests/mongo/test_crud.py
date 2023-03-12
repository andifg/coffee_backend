import asyncio

import pytest

from tests.conftest import TestDBSessions


@pytest.mark.asyncio
async def test_mongo_insert(init_mongo: TestDBSessions) -> None:
    print(type(init_mongo))

    async with await init_mongo.Async.start_session() as s:
        doc = {"_id": 123, "x": 1}
        await s.client["test_db"]["testcollection"].insert_one(doc)

        breakpoint()

    assert 1 == 1


@pytest.mark.asyncio
async def test_mongo_insert_two(init_mongo: TestDBSessions) -> None:
    print(type(init_mongo))

    breakpoint()

    async with await init_mongo.Async.start_session() as s:
        doc = {"_id": 1234, "x": 1}
        await s.client["test_db"]["testcollection"].insert_one(doc)

        breakpoint()

    assert 1 == 1
