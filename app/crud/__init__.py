"""
CRUD operations for the historical figures API.

This module provides data access layer operations separated by entity type.
Each module contains CRUD operations for a specific database table.
"""

from .event import EventCRUD
from .person import PersonCRUD
from .tag import TagCRUD

__all__ = [
    # CRUD classes
    "EventCRUD",
    "PersonCRUD",
    "TagCRUD",
]
