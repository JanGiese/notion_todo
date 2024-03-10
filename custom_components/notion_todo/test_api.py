"""Test cases for the Notion API client."""
import os
import aiohttp
import unittest
from custom_components.notion_todo.api import NotionApiClient

TITLE = "title"
TITLE_UPDATED = TITLE + '_updated'
NOT_STARTED = 'not-started'
DONE = "done"
DESCRIPTION = "test"
DUE = "2024-01-01"

TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

class TestApi(unittest.IsolatedAsyncioTestCase):
    """Test cases for the Notion API client."""

    # delete all tasks before running tests
    async def asyncSetUp(self):
        """Set up the test environment."""
        async with aiohttp.ClientSession() as session:
            client = NotionApiClient(TOKEN, DATABASE_ID, session)
            data = await client.async_get_data()
            for task in data['results']:
                await client.delete_task(task['id'])

    async def __create_task(self, client):
        """Create a task for testing and return its uid."""
        result = await client.create_task(TITLE, NOT_STARTED)
        uid = result['id']
        return uid

    async def test_create_task_returns_expected_result(self):
        """Test creating a task."""
        async with aiohttp.ClientSession() as session:
            client = NotionApiClient(TOKEN, DATABASE_ID, session)

            result = await client.create_task(TITLE, NOT_STARTED)

            assert 'id' in result

    async def test_delete_task_returns_expected_result(self):
        """Test deleting a task."""
        async with aiohttp.ClientSession() as session:
            client = NotionApiClient(TOKEN, DATABASE_ID, session)
            uid = await self.__create_task(client)

            result = await client.delete_task(uid)

            assert result["id"] == uid

    async def test_get_data_returns_expected_result(self):
        """Test getting data from the database."""
        async with aiohttp.ClientSession() as session:
            client = NotionApiClient(TOKEN, DATABASE_ID, session)
            uid = await self.__create_task(client)

            result = await client.async_get_data()

            assert uid == result['results'][0]['id']

    async def test_update_task_returns_expected_result(self):
        """Test updating a task."""
        async with aiohttp.ClientSession() as session:
            client = NotionApiClient(TOKEN, DATABASE_ID, session)
            uid = await self.__create_task(client)

            result = await client.update_task(uid, TITLE_UPDATED, DONE, DUE, DESCRIPTION)

            assert result["properties"]["Task name"]["title"][0]["text"]["content"] == TITLE_UPDATED
            assert result["properties"]["Status"]["status"]["id"] == DONE
            assert result["properties"]["Due"]["date"]["start"] == DUE
            assert result["properties"]["Summary"]["rich_text"][0]["text"]["content"] == DESCRIPTION

    async def test_update_given_no_due_date_should_return_expected_result(self):
        """Test updating a task without a due date."""
        async with aiohttp.ClientSession() as session:
            client = NotionApiClient(TOKEN, DATABASE_ID, session)
            uid = await self.__create_task(client)

            result = await client.update_task(uid, TITLE_UPDATED, DONE, None, DESCRIPTION)

            assert result["properties"]["Task name"]["title"][0]["text"]["content"] == TITLE_UPDATED
            assert result["properties"]["Status"]["status"]["id"] == DONE
            assert result["properties"]["Summary"]["rich_text"][0]["text"]["content"] == DESCRIPTION
