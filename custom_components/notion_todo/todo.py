"""A todo platform for Notion."""

import asyncio
from typing import cast

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TASK_STATUS_PROPERTY, TASK_DESCRIPTION_PROPERTY, TASK_DATE_PROPERTY
from .coordinator import NotionDataUpdateCoordinator
from .notion_property_helper import NotionPropertyHelper as propHelper

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the todo platform config entry."""
    coordinator: NotionDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = ['Notion']
    async_add_entities(
        NotionTodoListEntity(coordinator, e)
        for e in entities
    )

STATUS_IN_PROGRESS = 'in-progress'
STATUS_ARCHIVED = 'archived'
STATUS_DONE = 'done'
STATUS_NOT_STARTED = 'not-started'
NOTION_TO_HASS_STATUS = {
    STATUS_NOT_STARTED: TodoItemStatus.NEEDS_ACTION,
    STATUS_IN_PROGRESS: TodoItemStatus.NEEDS_ACTION,
    STATUS_DONE: TodoItemStatus.COMPLETED,
    STATUS_ARCHIVED: TodoItemStatus.COMPLETED
}
HASS_TO_NOTION_STATUS = {
    TodoItemStatus.NEEDS_ACTION: STATUS_NOT_STARTED,
    TodoItemStatus.COMPLETED: STATUS_DONE
}

class NotionTodoListEntity(CoordinatorEntity[NotionDataUpdateCoordinator], TodoListEntity):
    """A Notion TodoListEntity."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM
        | TodoListEntityFeature.SET_DUE_DATETIME_ON_ITEM
    )

    def __init__(
        self,
        coordinator: NotionDataUpdateCoordinator,
        user: str,
    ) -> None:
        """Initialize TodoListEntity."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"{user}-{user}"
        self._attr_name = user
        self._status = {}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_todo_items = None
        else:
            items = []
            for task in self.coordinator.data['results']:
                id = task['id']
                self._status[id] = propHelper.get_property_by_id(TASK_STATUS_PROPERTY, task)
                status = NOTION_TO_HASS_STATUS[self._status[id]]

                items.append(
                    TodoItem(
                        summary=propHelper.get_property_by_id('title', task),
                        uid=id,
                        status=status,
                        description=propHelper.get_property_by_id(TASK_DESCRIPTION_PROPERTY, task),
                        due=propHelper.get_property_by_id(TASK_DATE_PROPERTY, task)
                    )
                )
            self._attr_todo_items = items
        super()._handle_coordinator_update()

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a To-do item."""
        await self.coordinator.client.create_task(item.summary, status=HASS_TO_NOTION_STATUS[item.status])
        await self.coordinator.async_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update a To-do item."""
        uid: str = cast(str, item.uid)
        status = HASS_TO_NOTION_STATUS[item.status]
        if self._status[uid] == STATUS_IN_PROGRESS and status == STATUS_NOT_STARTED:
            status = STATUS_IN_PROGRESS
        if self._status[uid] == STATUS_ARCHIVED and status == STATUS_DONE:
            status = STATUS_ARCHIVED

        await self.coordinator.client.update_task(task_id=uid,
                                                  title=item.summary,
                                                  status=status,
                                                  due=item.due,
                                                  description=item.description)

        await self.coordinator.async_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete a To-do item."""
        await asyncio.gather(
            *[self.coordinator.client.delete_task(task_id=uid) for uid in uids]
        )
        await self.coordinator.async_refresh()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass update state from existing coordinator data."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
