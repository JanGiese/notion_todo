"""Notion API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

from .const import NOTION_URL, NOTION_VERSION, TASK_STATUS_PROPERTY, TASK_ASSIGNEE_PROPERTY, TASK_DATE_PROPERTY, TASK_SUMMARY_PROPERTY
from .notion_property_helper import NotionPropertyHelper as propHelper


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
        self._task_template = None

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="post",
            url=f"{NOTION_URL}/databases/{self._database_id}/query",
            headers=self._headers
        )

    async def update_task(
        self,
        task_id: str,
        title: str,
        status: str,
    ) -> any:
        """Update task in Notion.

        Args:
            task_id (str): id of the task
            title: (str): Title of the task
            status (str): Status of the task
        """
        task_template = await self._get_task_template()
        task_data = task_template.copy()
        task_data = propHelper.set_property_by_id("title", title, task_data)
        task_data = propHelper.set_property_by_id(TASK_STATUS_PROPERTY, status, task_data)
        task_data = propHelper.del_property_by_id(TASK_ASSIGNEE_PROPERTY, task_data)
        task_data = propHelper.del_property_by_id(TASK_DATE_PROPERTY, task_data)
        task_data = propHelper.del_property_by_id(TASK_SUMMARY_PROPERTY, task_data)
        update_properties = task_data['properties']
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
        task_template = await self._get_task_template()
        task_data = task_template.copy()
        task_data = propHelper.set_property_by_id("title", title, task_data)
        task_data = propHelper.set_property_by_id(TASK_STATUS_PROPERTY, status, task_data)
        task_data = propHelper.del_property_by_id(TASK_ASSIGNEE_PROPERTY, task_data)
        task_data = propHelper.del_property_by_id(TASK_DATE_PROPERTY, task_data)
        task_data = propHelper.del_property_by_id(TASK_SUMMARY_PROPERTY, task_data)

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

    async def _get_database(self):
        return await self._api_wrapper(
            method="get",
            url=f"{NOTION_URL}/databases/{self._database_id}",
            headers=self._headers
        )

    async def _init_task_template(self):
        self._database = await self._get_database()
        self._task_template = {
            'parent': {'database_id': self._database_id},
            'properties': self._database['properties']
        }
        return self._task_template

    async def _get_task_template(self):
        if self._task_template:
            return self._task_template
        return await self._init_task_template()

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
