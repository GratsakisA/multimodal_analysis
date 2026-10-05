# src/repository_name/data/processors.py
"""
Low-level data processing functions.

This module contains functions that process raw trial data from the database,
including filtering, aggregating, and computing statistics on trials.
"""

import pandas as pd
import numpy as np
from ..stimuli.objects import OBJECT_ALIASES
from ..stimuli.tones import AUDITORY_TRIAL_CRITERIA, MULTIMODAL_AUDITORY_CRITERIA


def process_visual_object(animal_id, obj_id, sessions, difficulties, 
                          excluded_sessions, stim, exp):
    """Process visual trials for a specific object across sessions.
    
    Fetches all visual trials (tone_volume=0) for a given object and computes
    performance metrics per session. Visual trials are defined as auditory
    trials with NO visual component (obj_mag == 0 is auditory-only).
    
    Args:
        animal_id (str): Animal identifier.
        obj_id (int): Object ID to process.
        sessions (numpy.ndarray): Array of session numbers to process.
        difficulties (list): List of difficulty levels to include.
        excluded_sessions (set): Set of session numbers to exclude.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        pd.DataFrame: DataFrame with columns:
            - animal_id: Animal identifier
            - session: Session number
            - date: Session date
            - session_trials: Total trials in session
            - valid_obj_trials: Valid trials for this object
            - performance: Reward / (Reward + Punish)
            - reward: Number of reward trials
            - punish: Number of punish trials
            - abort: Number of abort trials
            
    Example:
        >>> from db import get_schemas
        >>> schemas = get_schemas()
        >>> exp = schemas['exp']
        >>> stim = schemas['stim']
        >>> df = process_visual_object('mouse_1', 211, sessions, [1, 2], {}, stim, exp)
    """
    rows = []
    
    difficulty_filter = [{'difficulty': d} for d in difficulties]

    for session in sessions:
        
        if session in excluded_sessions:
            continue
            
        key_session = {'animal_id': animal_id, 'session': session}

        session_date = (exp.Session() & key_session).fetch1(
            'session_tmst'
        ).strftime('%Y-%m-%d')
        
        # Handle object aliases
        obj_ids = OBJECT_ALIASES.get(obj_id, [obj_id])
        obj_query = ' OR '.join([f'obj_id={o}' for o in obj_ids])
        
        # Fetch visual trials (tone_volume = 0)
        # See AUDITORY_TRIAL_CRITERIA for criteria definition
        visual_trials = pd.DataFrame(
            (
                stim.StimCondition.Trial()
                * stim.Tones
                * exp.Trial
                * exp.Condition.MatchPort
                * stim.Panda.Object
                & key_session
                & obj_query
                & difficulty_filter
                & 'tone_volume=0'
            ).fetch(as_dict=True)
        )
        
        if visual_trials.empty:
            continue
        
        # Get trial states
        visual_keys = visual_trials.to_dict('records')
        state_visual = pd.DataFrame(
            (exp.Trial.StateOnset & key_session & visual_keys).fetch(
                'state', 
                as_dict=True
            )
        )
        
        total_trials = len(exp.Trial & key_session)
        
        rew = (state_visual['state'] == 'Reward').sum()
        pun = (state_visual['state'] == 'Punish').sum()
        
        valid = rew + pun
        performance = round(rew / valid, 2) if valid else 0
        
        rows.append({
            'animal_id': animal_id,
            'session': session,
            'date': session_date,
            'session_trials': total_trials,
            'valid_obj_trials': valid,
            'performance': performance,
            'reward': rew,
            'punish': pun,
            'abort': (state_visual['state'] == 'Abort').sum()
        })
    
    return pd.DataFrame(rows)


def process_multimodal_object(animal_id, obj_id, sessions, difficulties,
                              excluded_sessions, stim, exp):
    """Process multimodal trials for a specific object across sessions.
    
    Fetches all multimodal trials (tone_volume > 0, obj_mag > 0) for a given
    object and computes performance metrics per session. Multimodal trials
    contain both auditory and visual stimulus components.
    
    See MULTIMODAL_AUDITORY_CRITERIA in stimuli.tones for criteria definition.
    
    Args:
        animal_id (str): Animal identifier.
        obj_id (int): Object ID to process.
        sessions (numpy.ndarray): Array of session numbers to process.
        difficulties (list): List of difficulty levels to include.
        excluded_sessions (set): Set of session numbers to exclude.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        pd.DataFrame: DataFrame with columns:
            - animal_id: Animal identifier
            - session: Session number
            - date: Session date
            - session_trials: Total trials in session
            - valid_obj_trials: Valid trials for this object
            - percentage: Percentage of session trials
            - performance: Reward / (Reward + Punish)
            - reward: Number of reward trials
            - punish: Number of punish trials
            - abort: Number of abort trials
            
    Example:
        >>> df = process_multimodal_object('mouse_1', 211, sessions, [1, 2], {}, stim, exp)
    """
    rows = []

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')

    for session in sessions:

        if session in excluded_sessions:
            continue

        key_session = {'animal_id': animal_id, 'session': session}
        
        session_date = (exp.Session() & key_session).fetch1(
            'session_tmst'
        ).strftime('%Y-%m-%d')

        # Handle object aliases
        obj_ids = OBJECT_ALIASES.get(obj_id, [obj_id])
        obj_query = ' OR '.join([f'obj_id={o}' for o in obj_ids])

        # Fetch multimodal trials (tone_volume > 0 AND obj_mag > 0)
        # Criteria: both auditory and visual stimuli present
        multi_trials = pd.DataFrame(
            (
                stim.StimCondition.Trial
                * stim.Panda.Object.proj('obj_mag')
                * exp.Trial.StateOnset
                * difficulty
                * stim.Tones.proj('tone_volume')
                & key_session
                & obj_query
                & difficulty_filter
                & 'tone_volume > 0'
                & 'state in ("Reward", "Punish", "Abort")'
            ).fetch(as_dict=True)
        )

        if multi_trials.empty:
            continue

        multi_trials['obj_mag'] = pd.to_numeric(
            multi_trials['obj_mag'],
            errors='coerce'
        )

        # Filter by object magnitude > 0
        multi_trials = multi_trials[multi_trials['obj_mag'] > 0]

        if multi_trials.empty:
            continue

        total_trials = len(exp.Trial & key_session)

        rew = (multi_trials['state'] == 'Reward').sum()
        pun = (multi_trials['state'] == 'Punish').sum()
        abrt = (multi_trials['state'] == 'Abort').sum()

        valid = rew + pun
        performance = round(rew / valid, 2) if valid else 0

        percentage = (
            round((valid / total_trials) * 100, 2)
            if total_trials else 0
        )

        rows.append({
            'animal_id': animal_id,
            'session': session,
            'date': session_date,
            'session_trials': total_trials,
            'valid_obj_trials': valid,
            'percentage': percentage,
            'performance': performance,
            'reward': rew,
            'punish': pun,
            'abort': abrt
        })

    return pd.DataFrame(rows)