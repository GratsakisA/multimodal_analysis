"""
Validation utilities for input parameters and keys.

This module contains functions to validate and process user inputs
like analysis keys and difficulty levels.
"""


def validate_key(key):
    """Validate that a key dictionary contains all required fields.
    
    Args:
        key (dict): Analysis key dictionary to validate.
        
    Raises:
        KeyError: If required fields are missing.
        
    Example:
        >>> key = {'animal_id': 'mouse_1', 'sessions': (1, 10)}
        >>> validate_key(key)
    """
    required = ['animal_id', 'sessions']
    
    for field in required:
        if field not in key:
            raise KeyError(f"Missing required key: '{field}'")


def get_difficulties(key):
    """Extract and validate difficulty levels from key dictionary.
    
    Converts single difficulty values to a list format for consistency.
    Returns None if no difficulties are specified.
    
    Args:
        key (dict): Dictionary that may contain 'difficulties' key.
        
    Returns:
        list or None: List of difficulty levels, or None if not specified.
        
    Example:
        >>> key = {'difficulties': 2}
        >>> get_difficulties(key)
        [2]
        
        >>> key = {'difficulties': [1, 2, 3]}
        >>> get_difficulties(key)
        [1, 2, 3]
    """
    difficulties = key.get('difficulties')
    
    # Check if difficulties is None or empty
    if difficulties is None or (
        hasattr(difficulties, '__len__') and len(difficulties) == 0
    ):
        print("⚠️ Please specify difficulty level(s)")
        return None
    
    # Convert single number to list
    if isinstance(difficulties, (int, float)):
        return [difficulties]
    
    # Already a list or tuple
    return list(difficulties)