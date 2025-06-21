"""
CRUD operations for the historical figures API.

This module provides data access layer operations separated by entity type.
Each module contains CRUD operations for a specific database table.
"""

from .event import (
    create_event,
    delete_event,
    get_event,
    get_event_by_ssid,
    get_events,
    update_event,
)
from .person import (
    create_person,
    delete_person,
    get_person,
    get_person_by_ssid,
    get_persons,
    update_person,
)
from .tag import (
    create_tag,
    delete_tag,
    get_tag,
    get_tag_by_ssid,
    get_tags,
    update_tag,
)

__all__ = [
    # Person operations
    "create_person",
    "get_person",
    "get_person_by_ssid",
    "get_persons",
    "update_person",
    "delete_person",
    # Tag operations
    "create_tag",
    "get_tag",
    "get_tag_by_ssid",
    "get_tags",
    "update_tag",
    "delete_tag",
    # Event operations
    "create_event",
    "get_event",
    "get_event_by_ssid",
    "get_events",
    "update_event",
    "delete_event",
]
