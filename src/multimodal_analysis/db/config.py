"""
Database configuration and schema setup.

This module handles DataJoint connection settings and schema initialization.
"""

import os
import datajoint as dj

# database configuration 
dj.config['database.password'] = os.getenv('DJ_PASSWORD')
dj.config['database.host'] = 'database.eflab.org:3306'
dj.config["enable_python_native_blobs"] = True

# schema configuration 
SCHEMATA = {
    'exp': 'lab_experiments',
    'stim': 'lab_stimuli',
    'beh': 'lab_behavior',
    'inter': 'lab_interface',
    'rec': 'lab_recordings',
    'mice': 'lab_mice'
}

def get_schemas():
    """Initialize and return all virtual DataJoint schemas.
    
    Creates virtual modules for all configured schemas. These modules
    provide access to the DataJoint tables without local definitions.
    
    Returns:
        dict: Dictionary mapping schema names to virtual modules.
            Keys are: 'exp', 'stim', 'beh', 'inter', 'rec', 'mice'.
        
    Example:
        >>> from db.config import get_schemas
        >>> schemas = get_schemas()
        >>> exp = schemas['exp']
        >>> sessions = exp.Session.fetch()
    """
    schemata = {}
    for schema_key, schema_name in SCHEMATA.items():
        schemata[schema_key] = dj.create_virtual_module(
            schema_key, 
            schema_name, 
            create_tables=True, 
            create_schema=True
        )
    return schemata

def get_schema_modules():
    """Initialize and return all schemas as individual modules."""
    schemas = get_schemas()

    return (
        schemas["exp"],
        schemas["stim"],
        schemas["beh"],
        schemas["inter"],
        schemas["rec"],
        schemas["mice"],
    )