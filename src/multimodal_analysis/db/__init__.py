"""Database module for DataJoint connections and schemas.

Handles all database configuration and schema initialization.
"""

from .config import get_schemas, SCHEMATA, get_schema_modules

__all__ = ['get_schemas', 'SCHEMATA','get_schema_modules']