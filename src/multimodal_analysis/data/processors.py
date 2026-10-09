"""
Low-level data processing functions.

This module contains functions that process raw trial data from the database,
including filtering, aggregating, and computing statistics on trials.
"""

import pandas as pd
import numpy as np
from ..stimuli.objects import object_aliases
from ..stimuli.tones import auditory_trial_criteria, multimodal_auditory_criteria 


def process_visual_object(animal_id, obj_id, sessions, difficulties, 
                          excluded_sessions, stim, exp):
    """Process visual trials for a specific object across sessions.
    
    Fetches all visual trials (tone_volume=0) for a given object and computes
    performance metrics per session.
    
    Args:
        animal_id (str): Animal identifier.
        obj_id (int): Object ID to process.
        sessions (numpy.ndarray): Array of session numbers to process.
        difficulties (list): List of difficulty levels to include.
        excluded_sessions (set): Set of session numbers to exclude.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        pd.DataFrame: DataFrame with columns for animal_id, session, date, etc.
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
        obj_ids = object_aliases.get(obj_id, [obj_id])
        obj_query = ' OR '.join([f'obj_id={o}' for o in obj_ids])
        
        # Fetch visual trials with state in one query
        visual_trials = (
            stim.StimCondition.Trial
            * (stim.Panda.Object).proj('obj_mag')
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume')
            & key_session
            & obj_query
            & difficulty_filter
            & 'tone_volume=0'
            & 'state in ("Reward", "Punish", "Abort")'
        ).fetch(format='frame').reset_index()
        
        if visual_trials.empty:
            continue
        
        visual_trials['obj_mag'] = pd.to_numeric(
            visual_trials['obj_mag'], 
            errors='coerce'
        )
        visual_trials = visual_trials[visual_trials['obj_mag'] > 0]
        
        if visual_trials.empty:
            continue
        
        total_trials = len(exp.Trial & key_session)
        
        rew = (visual_trials['state'] == 'Reward').sum()
        pun = (visual_trials['state'] == 'Punish').sum()
        
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
            'abort': (visual_trials['state'] == 'Abort').sum()
        })
    
    return pd.DataFrame(rows)


def process_multimodal_object(animal_id, obj_id, sessions, difficulties,
                              excluded_sessions, stim, exp):
    """Process multimodal trials for a specific object across sessions.
    
    Fetches all multimodal trials (tone_volume > 0, obj_mag > 0) for a given
    object and computes performance metrics per session.
    
    Args:
        animal_id (str): Animal identifier.
        obj_id (int): Object ID to process.
        sessions (numpy.ndarray): Array of session numbers to process.
        difficulties (list): List of difficulty levels to include.
        excluded_sessions (set): Set of session numbers to exclude.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        pd.DataFrame: DataFrame with columns for animal_id, session, date, etc.
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

        # Fetch multimodal trials with state in one query
        multi_trials = (
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
        ).fetch(format='frame').reset_index()

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