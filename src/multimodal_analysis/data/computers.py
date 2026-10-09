"""
Data computation functions for analysis.

This module contains functions that compute statistics and metrics
from processed trial data, with integration of stimulus configurations.
"""

import pandas as pd
import numpy as np
from ..utils.validators import get_difficulties
from ..utils.queries import fetch_sessions
from ..stimuli.tones import (
    tone_pulse_frequencies, 
    tone_pulse_freq_names,
    auditory_trial_criteria,
    multimodal_auditory_criteria
)


def compute_auditory_performance_summary(key, stim, exp):
    """Compute auditory performance for different tone frequencies.
    
    Separates auditory trials by tone pulse frequency (continuous vs pulsed)
    and computes performance metrics for each. Uses tone configurations
    from stimuli.tones module.
    
    Args:
        key (dict): Analysis key dictionary with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session) range
            - difficulties (int or list): Difficulty level(s)
            - excluded_sessions (set, optional): Sessions to exclude
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        tuple: (pulse0_df, pulse100_df) where each is a DataFrame with columns:
            - animal_id: Animal identifier
            - session: Session number
            - date: Session date
            - performance: Reward / (Reward + Punish)
            - reward: Count of reward trials
            - punish: Count of punish trials
            - abort: Count of abort trials
            - n_trials: Total trials of this type
            - tone_pulse_freq: Tone pulse frequency (0 or 100 Hz)
            
    Example:
        >>> key = {
        ...     'animal_id': 'mouse_1',
        ...     'sessions': (1, 20),
        ...     'difficulties': [1, 2],
        ...     'excluded_sessions': set()
        ... }
        >>> pulse0_df, pulse100_df = compute_auditory_performance_summary(key, stim, exp)
        >>> print(pulse0_df)  # Continuous tone data
        >>> print(pulse100_df)  # Pulsed tone data
    """
    animal_id = key['animal_id']
    from_session, to_session = key['sessions']
    
    difficulties = get_difficulties(key)
    if difficulties is None:
        return pd.DataFrame(), pd.DataFrame()
    
    excluded_sessions = key.get('excluded_sessions', set())
    
    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')
    
    restr = exp.Session() & {'animal_id': animal_id}
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')
    
    rows_pulse0 = []
    rows_pulse100 = []
    
    for session in range(from_session, to_session + 1):
    
        if session not in valid_sessions:
            continue

        if session in excluded_sessions:
            continue
    
        key_session = {'animal_id': animal_id, 'session': session}
    
        session_date = (exp.Session() & key_session).fetch1(
            'session_tmst'
        ).strftime('%Y-%m-%d')
    
        # Fetch auditory trials using criteria from stimuli.tones
        # Auditory trials: tone_volume > 0 AND obj_mag == 0
        auditory_trials = (
            stim.StimCondition.Trial
            * (stim.Panda.Object).proj('obj_mag')
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume', 'tone_pulse_freq')
            & 'tone_volume > 0'
            & key_session
            & difficulty_filter
            & 'state in ("Reward", "Punish", "Abort")'
        ).fetch(format='frame').reset_index()
    
        auditory_trials['obj_mag'] = pd.to_numeric(
            auditory_trials['obj_mag'], 
            errors='coerce'
        )
        auditory_trials = auditory_trials[auditory_trials['obj_mag'] == 0]
    
        # Separate by tone frequency using tone_pulse_frequencies
        continuous_tone_freq = tone_pulse_frequencies[0]  # 0 Hz
        pulsed_tone_freq = tone_pulse_frequencies[1]      # 100 Hz
        
        pulse0 = auditory_trials[
            auditory_trials['tone_pulse_freq'] == continuous_tone_freq
        ]
        pulse100 = auditory_trials[
            auditory_trials['tone_pulse_freq'] == pulsed_tone_freq
        ]
    
        # Process both tone types
        for df_trials, rows, freq in [
            (pulse0, rows_pulse0, continuous_tone_freq), 
            (pulse100, rows_pulse100, pulsed_tone_freq)
        ]:

            if df_trials.empty:
                continue
    
            reward = (df_trials['state'] == 'Reward').sum()
            punish = (df_trials['state'] == 'Punish').sum()
            abort = (df_trials['state'] == 'Abort').sum()
    
            perf = (
                round(reward / (reward + punish), 2)
                if (reward + punish) > 0 else np.nan
            )
    
            rows.append({
                'animal_id': animal_id,
                'session': session,
                'date': session_date,
                'performance': perf,
                'reward': reward,
                'punish': punish,
                'abort': abort,
                'n_trials': len(df_trials),
                'tone_pulse_freq': freq,
                'tone_type': tone_pulse_freq_names[freq]  # Human-readable name
            })

    pulse0_df = pd.DataFrame(rows_pulse0)
    pulse100_df = pd.DataFrame(rows_pulse100)

    return pulse0_df, pulse100_df


def compute_modality_performance(animal_id, from_session, to_session, stim, 
                                 exp, excluded_sessions, difficulties):
    """Compute performance across different stimulus modalities.
    
    Compares performance in auditory, visual, and multimodal conditions,
    including difficult variants. Integrates stimulus definitions from
    stimuli.tones and stimuli.objects modules.
    
    Args:
        animal_id (str): Animal identifier.
        from_session (int): Start session number (inclusive).
        to_session (int): End session number (inclusive).
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        excluded_sessions (list or set): Session numbers to exclude.
        difficulties (list): List of difficulty levels to include.
        
    Returns:
        pd.DataFrame: DataFrame with columns:
            - session: Session number
            - auditory_perf: Auditory performance (NaN if no trials)
            - visual_perf: Visual performance (NaN if no trials)
            - multi_perf: Multimodal performance (NaN if no trials)
            - multi_difficult_perf: Multimodal difficult performance
            - visual_difficult_perf: Visual difficult performance
            
    Example:
        >>> df = compute_modality_performance(
        ...     'mouse_1', 1, 20, stim, exp, set(), [1, 2]
        ... )
        >>> print(df)
    """
    difficulties = get_difficulties({'difficulties': difficulties})
    if difficulties is None:
        return pd.DataFrame()

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')

    restr = exp.Session() & {'animal_id': animal_id}
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')

    perf_per_condition = []

    for session in range(from_session, to_session + 1):

        if session not in valid_sessions or session in excluded_sessions:
            continue

        key = {'animal_id': animal_id, "session": session}

        # AUDITORY TRIALS
        # Using AUDITORY_TRIAL_CRITERIA: tone_volume > 0 AND obj_mag == 0
        auditory_trials = (
            stim.StimCondition.Trial
            * (stim.Panda.Object).proj('obj_mag')
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume')
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()

        auditory_trials['obj_mag'] = pd.to_numeric(
            auditory_trials['obj_mag'], 
            errors='coerce'
        )
        auditory_trials = auditory_trials[auditory_trials['obj_mag'] == 0]

        # VISUAL TRIALS
        # Visual: tone_volume = 0 AND obj_mag > 0 (non-difficult objects)
        visual_trials = (
            stim.StimCondition.Trial
            * (stim.Panda.Object).proj('obj_mag')
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume')
            & 'tone_volume = 0'
            & key
            & 'obj_id NOT IN (214, 215, 216, 217)'
            & difficulty_filter
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()

        visual_trials['obj_mag'] = pd.to_numeric(
            visual_trials['obj_mag'], 
            errors='coerce'
        )
        visual_trials = visual_trials[visual_trials['obj_mag'] > 0]

        # MULTIMODAL TRIALS
        # Using MULTIMODAL_AUDITORY_CRITERIA: tone_volume > 0 AND obj_mag > 0
        multi_trials = (
            stim.StimCondition.Trial
            * (stim.Panda.Object).proj('obj_mag')
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume')
            & 'tone_volume > 0'
            & key
            & 'obj_id NOT IN (214, 215, 216, 217)'
            & difficulty_filter
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()

        multi_trials['obj_mag'] = pd.to_numeric(
            multi_trials['obj_mag'], 
            errors='coerce'
        )
        multi_trials = multi_trials[multi_trials['obj_mag'] > 0]

        # DIFFICULT MULTIMODAL TRIALS
        # Multimodal with difficult objects: tone_volume > 0 AND obj_mag > 0
        # AND obj_id IN (214, 216, 217)
        multi_difficult_trials = (
            stim.StimCondition.Trial
            * (stim.Panda.Object).proj('obj_mag')
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume')
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'obj_id IN (214, 216, 217)'
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()
        
        multi_difficult_trials['obj_mag'] = pd.to_numeric(
            multi_difficult_trials['obj_mag'], 
            errors='coerce'
        )
        multi_difficult_trials = multi_difficult_trials[
            multi_difficult_trials['obj_mag'] > 0
        ]

        # DIFFICULT VISUAL TRIALS
        # Visual with difficult objects: tone_volume = 0 AND obj_mag > 0
        # AND obj_id IN (214, 216, 217)
        visual_difficult_trials = (
            stim.StimCondition.Trial
            * (stim.Panda.Object).proj('obj_mag')
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume')
            & 'tone_volume = 0'
            & key
            & difficulty_filter
            & 'obj_id IN (214, 216, 217)'
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()
        
        visual_difficult_trials['obj_mag'] = pd.to_numeric(
            visual_difficult_trials['obj_mag'], 
            errors='coerce'
        )
        visual_difficult_trials = visual_difficult_trials[
            visual_difficult_trials['obj_mag'] > 0
        ]

        # Skip session if no trials in any condition
        if (
            len(auditory_trials) == 0 and
            len(visual_trials) == 0 and
            len(multi_trials) == 0 and
            len(multi_difficult_trials) == 0 and
            len(visual_difficult_trials) == 0
        ):
            continue

        # Compute performance for each modality
        perf_per_condition.append({
            'session': session,
            'auditory_perf': (
                round((auditory_trials['state'] == 'Reward').mean(), 2)
                if len(auditory_trials) > 0 else np.nan
            ),
            'visual_perf': (
                round((visual_trials['state'] == 'Reward').mean(), 2)
                if len(visual_trials) > 0 else np.nan
            ),
            'multi_perf': (
                round((multi_trials['state'] == 'Reward').mean(), 2)
                if len(multi_trials) > 0 else np.nan
            ),
            'multi_difficult_perf': (
                round((multi_difficult_trials['state'] == 'Reward').mean(), 2)
                if len(multi_difficult_trials) > 0 else np.nan
            ),
            'visual_difficult_perf': (
                round((visual_difficult_trials['state'] == 'Reward').mean(), 2)
                if len(visual_difficult_trials) > 0 else np.nan
            )
        })

    return pd.DataFrame(perf_per_condition)