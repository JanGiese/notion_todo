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

from .const import DOMAIN
from .coordinator import NotionDataUpdateCoordinator


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

# TODO use internal status for In Progress
NOTION_TO_HASS_STATUS = {
    'Not started': TodoItemStatus.NEEDS_ACTION,
    'Done': TodoItemStatus.COMPLETED
}
HASS_TO_NOTION_STATUS = {
    TodoItemStatus.NEEDS_ACTION: 'Not started',
    TodoItemStatus.COMPLETED: 'Done'
}

class NotionTodoListEntity(CoordinatorEntity[NotionDataUpdateCoordinator], TodoListEntity):
    """A Notion TodoListEntity."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
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
        self.dummy_tasks = [{'summary':'TestTask', 'status': TodoItemStatus.NEEDS_ACTION}]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_todo_items = None
        else:
            items = []
            for task in self.coordinator.data['results']:
                status = NOTION_TO_HASS_STATUS[task['properties']['Status']['status']['name']]

                items.append(
                    TodoItem(
                        summary=task['properties']['Name']['title'][0]['plain_text'],
                        uid=task['id'],
                        status=status,
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
        update_properties={}
        if item.summary:
            update_properties['Name'] = {
            "title": [
                {
                    "text": {
                        "content": item.summary
                    }
                }
            ]
        }
        if item.status is not None:
            if item.status == TodoItemStatus.COMPLETED:
                update_properties['Status'] = {
                    'status': {
                        'name': "Done"
                    }
                }
            else:
                update_properties['Status'] = {
                    'status': {
                        'name': "Not started"
                    }
                }
        if update_properties != {}:
            await self.coordinator.client.update_task(task_id=uid, update_properties=update_properties)

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
