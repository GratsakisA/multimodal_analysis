"""
Data fetching functions for analysis.

This module contains high-level functions for fetching processed data
organized by modality (visual, auditory, multimodal).
"""

import pandas as pd
from ..utils.validators import validate_key, get_difficulties
from ..utils.queries import fetch_sessions
from ..stimuli.objects import DEFAULT_OBJECT_IDS
from .processors import process_visual_object, process_multimodal_object


def fetch_visual_data(key, stim, exp):
    """Fetch object-wise visual performance data.
    
    Processes visual trials for all objects and returns a dictionary
    of DataFrames, one per object.
    
    Args:
        key (dict): Analysis key dictionary with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session) range
            - difficulties (int or list): Difficulty level(s)
            - object_ids (list, optional): Object IDs to fetch. 
              Defaults to DEFAULT_OBJECT_IDS
            - excluded_sessions (set, optional): Sessions to exclude.
              Defaults to empty set
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        dict: Dictionary mapping object_id to pd.DataFrame.
            Only includes objects with trials. Empty dict if no data found.
            
    Example:
        >>> from db import get_schemas
        >>> from data.fetchers import fetch_visual_data
        >>> schemas = get_schemas()
        >>> key = {
        ...     'animal_id': 'mouse_1',
        ...     'sessions': (1, 20),
        ...     'difficulties': [1, 2, 3],
        ...     'excluded_sessions': {5, 10}
        ... }
        >>> visual_dfs = fetch_visual_data(key, schemas['stim'], schemas['exp'])
    """
    validate_key(key)
    
    animal_id = key['animal_id']
    difficulties = get_difficulties(key)
    
    if difficulties is None:
        return {}
    
    object_ids = key.get('object_ids', DEFAULT_OBJECT_IDS)
    excluded_sessions = key.get('excluded_sessions', set())
    
    sessions = fetch_sessions(
        animal_id=animal_id,
        session_range=key.get('sessions'),
        exp=exp
    )

    object_dfs = {}
    
    for obj_id in object_ids:
        df = process_visual_object(
            animal_id=animal_id,
            obj_id=obj_id,
            sessions=sessions,
            difficulties=difficulties,
            excluded_sessions=excluded_sessions,
            stim=stim,
            exp=exp
        )
        
        if not df.empty:
            object_dfs[obj_id] = df
            
    return object_dfs


def fetch_multimodal_data(key, stim, exp):
    """Fetch object-wise multimodal performance data.
    
    Processes multimodal trials for all objects and returns a dictionary
    of DataFrames, one per object.
    
    Args:
        key (dict): Analysis key dictionary with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session) range
            - difficulties (int or list): Difficulty level(s)
            - object_ids (list, optional): Object IDs to fetch.
              Defaults to DEFAULT_OBJECT_IDS
            - excluded_sessions (set, optional): Sessions to exclude.
              Defaults to empty set
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        dict: Dictionary mapping object_id to pd.DataFrame.
            Only includes objects with trials. Empty dict if no data found.
            
    Example:
        >>> multimodal_dfs = fetch_multimodal_data(key, schemas['stim'], schemas['exp'])
    """
    validate_key(key)

    animal_id = key['animal_id']
    difficulties = get_difficulties(key)
    
    if difficulties is None:
        return {}

    object_ids = key.get('object_ids', DEFAULT_OBJECT_IDS)
    excluded_sessions = key.get('excluded_sessions', set())

    sessions = fetch_sessions(
        animal_id=animal_id,
        session_range=key.get('sessions'),
        exp=exp
    )

    object_dfs = {}

    for obj_id in object_ids:

        df = process_multimodal_object(
            animal_id=animal_id,
            obj_id=obj_id,
            sessions=sessions,
            difficulties=difficulties,
            excluded_sessions=excluded_sessions,
            stim=stim,
            exp=exp
        )

        if not df.empty:
            object_dfs[obj_id] = df

    return object_dfs