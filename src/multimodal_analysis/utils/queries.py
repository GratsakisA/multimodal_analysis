"""
Database query helper functions.

This module contains reusable functions for querying and fetching data
from the DataJoint database.
"""


def fetch_sessions(animal_id, session_range, exp):
    """Fetch valid sessions within a specified range for an animal.
    
    Automatically excludes sessions marked as excluded in the database.
    
    Args:
        animal_id (str): Animal identifier.
        session_range (tuple): Tuple of (from_session, to_session) 
            indicating inclusive range.
        exp: DataJoint schema for experiments (from db.config.get_schemas()).
        
    Returns:
        numpy.ndarray: Array of valid session numbers within the range.
        
    Example:
        >>> from db import get_schemas
        >>> from utils.queries import fetch_sessions
        >>> schemas = get_schemas()
        >>> exp = schemas['exp']
        >>> sessions = fetch_sessions('mouse_1', (1, 20), exp)
        >>> print(sessions)
        [1 2 3 4 6 7 8 9 10 ...]
    """
    from_s, to_s = session_range
    
    # Query sessions for this animal within the range
    restr = (
        exp.Session()
        & {'animal_id': animal_id}
        & f'session >= {from_s}'
        & f'session <= {to_s}'
    )
    
    # Exclude any sessions marked as excluded
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')
    
    return valid_sessions