"""
Object definitions and aliases for visual stimuli.

This module contains all object ID configurations and their alternative
identifiers used throughout the project for visual and multimodal trials.
"""

# Object configuration

DEFAULT_OBJECT_IDS = [211, 212, 213, 214, 215, 216, 217, 218, 219]
"""List of standard visual object IDs used in experiments."""

OBJECT_ALIASES = {
    211: [211, 1],      
    219: [219, 2]       
}
"""Mapping of primary object IDs to their alternative identifiers.

Some objects can be referred to by multiple IDs in the database.
This mapping allows the code to handle both representations.

Example:
    Object 211 can be referenced as either 211 or 1.
    Object 219 can be referenced as either 219 or 2.
"""