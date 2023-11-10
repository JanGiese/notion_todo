"""Notion API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

from .const import NOTION_URL, NOTION_VERSION
from .task_template import TASK_TEMPLATE
from .notion_query import QUERY

class NotionApiClientError(Exception):
    """Exception to indicate a general API error."""


class NotionApiClientCommunicationError(
    NotionApiClientError
):
    """Exception to indicate a communication error."""


class NotionApiClientAuthenticationError(
    NotionApiClientError
):
    """Exception to indicate an authentication error."""


class NotionApiClient:
    """Notion API Client."""

    _headers = {
        'Authorization': 'Bearer <TOKEN>',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
        }

    def __init__(
        self,
        token: str,
        database_id: str,
        task_owner: str,
        session: aiohttp.ClientSession
    ) -> None:
        """Notion API Client.

        Args:
            token (str): Notion token with access to ToDo database
            database_id (str): id of the ToDo database
            task_owner (str): Task owner to be assigned to new tasks
            session (aiohttp.ClientSession): the session
        """
        self._token = token
        self._session = session
        self._headers['Authorization'] = f'Bearer {token}'
        self._database_id = database_id
        self._task_owner = task_owner
        TASK_TEMPLATE['parent']['database_id'] = database_id

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="post",
            url=f"{NOTION_URL}/databases/{self._database_id}/query",
            headers=self._headers,
            data=QUERY
        )

    async def update_task(
        self,
        task_id: str,
        update_properties: dict
    ) -> any:
        """Update task in Notion.

        Args:
            task_id (str): id of the task
            update_properties (dict): properties to be updated
        """
        return await self._api_wrapper(
            method="patch",
            url=f"{NOTION_URL}/pages/{task_id}",
            headers=self._headers,
            data={"properties": update_properties}
        )

    async def create_task(self, title: str, status: str) -> any:
        """Create a new task in Notion.

        Args:
            title (str): Title of the task
            status (str): Status of the task
        """
        task_data=TASK_TEMPLATE.copy()
        task_data['properties']['Name']['title'][0]['text']['content'] = title
        task_data['properties']['Status']['status']['name'] = status
        return await self._api_wrapper(
            method="post",
            url=f"{NOTION_URL}/pages",
            headers=self._headers,
            data=task_data)

    async def delete_task(self,
                          task_id: str):
        """Delete a task in Notion.

        Args:
            task_id (str): id of the task

        Returns:
            _type_: _description_
        """
        return await self._api_wrapper(
            method="delete",
            url=f"{NOTION_URL}/blocks/{task_id}",
            headers=self._headers)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise NotionApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise NotionApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise NotionApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise NotionApiClientError(
                "Something really wrong happened!"
            ) from exception