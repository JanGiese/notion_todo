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

from .const import DOMAIN, LOGGER
from .coordinator import NotionDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the todo platform config entry."""
    coordinator: NotionDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    LOGGER.error("Hello World")
    users = ['Jan']
    async_add_entities(
        NotionTodoListEntity(coordinator, user)
        for user in users
    )

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
            for task in self.dummy_tasks:#self.coordinator.data:
                """
                if task.project_id != self._project_id:
                    continue
                if task.is_completed:
                    status = TodoItemStatus.COMPLETED
                else:
                    status = TodoItemStatus.NEEDS_ACTION
                    """
                items.append(
                    TodoItem(
                        summary=task['summary'],#task.content,
                        uid=task['summary'],#task.id,
                        status=task['status'],
                    )
                )
            self._attr_todo_items = items
        super()._handle_coordinator_update()

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a To-do item."""
        """
        if item.status != TodoItemStatus.NEEDS_ACTION:
            raise ValueError("Only active tasks may be created.")
        await self.coordinator.api.add_task(
            content=item.summary or "",
            project_id=self._project_id,
        )"""
        self.dummy_tasks.append({'summary': item.summary or "", 'status': TodoItemStatus.NEEDS_ACTION})
        await self.coordinator.async_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update a To-do item."""
        uid: str = cast(str, item.uid)
        """if item.summary:
            await self.coordinator.api.update_task(task_id=uid, content=item.summary)
        if item.status is not None:
            if item.status == TodoItemStatus.COMPLETED:
                await self.coordinator.api.close_task(task_id=uid)
            else:
                await self.coordinator.api.reopen_task(task_id=uid)"""
        #for i in self.dummy_items:
        #    if i.summary == item.summary:

        await self.coordinator.async_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete a To-do item."""
        """await asyncio.gather(
            *[self.coordinator.api.delete_task(task_id=uid) for uid in uids]
        )"""
        await self.coordinator.async_refresh()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass update state from existing coordinator data."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()