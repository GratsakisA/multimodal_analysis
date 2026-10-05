"""Database module for DataJoint connections and schemas.

Handles all database configuration and schema initialization.
"""

from .config import get_schemas, SCHEMATA

__all__ = ['get_schemas', 'SCHEMATA']