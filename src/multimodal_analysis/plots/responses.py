"""
Response type plotting functions.

This module contains functions for visualizing trial outcomes
(Reward, Punish, Abort) across sessions.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from ..utils.validators import validate_key, get_difficulties
from ..utils.queries import fetch_sessions


def calculate_response_type(animal_id, from_session, to_session, stim, exp,
                           excluded_sessions, difficulties):
    """Calculate response counts across all trial types.
    
    Counts the number of Reward, Punish, and Abort outcomes for each
    session across all trial modalities.
    
    Args:
        animal_id (str): Animal identifier.
        from_session (int): Start session number (inclusive).
        to_session (int): End session number (inclusive).
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        excluded_sessions (list or set): Session numbers to exclude.
        difficulties (int or list): Difficulty level(s) to include.
        
    Returns:
        pd.DataFrame: DataFrame with columns:
            - session: Session number
            - state: Response state ('Reward', 'Punish', 'Abort')
            - n_trials: Count of trials with this outcome
            
    Example:
        >>> df = calculate_response_type('mouse_1', 1, 20, stim, exp, set(), [1, 2])
        >>> print(df)
    """
    difficulties = get_difficulties({'difficulties': difficulties})
    
    if difficulties is None:
        return pd.DataFrame()

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')
        
    restr = exp.Session() & {'animal_id': animal_id}
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')

    rows = []

    for session in range(from_session, to_session + 1):
        if session not in valid_sessions:
            continue
        
        if session in excluded_sessions:
            continue
    
        key = {'animal_id': animal_id, "session": session}

        session_trials = (
            stim.StimCondition.Trial 
            * exp.Trial.StateOnset 
            * difficulty
            & difficulty_filter
            & key
            & 'state in ("Reward", "Punish", "Abort")'
        ).fetch(format='frame').reset_index()

        if session_trials.empty:
            continue

        for state in ['Reward', 'Punish', 'Abort']:
            rows.append({
                'session': session,
                'state': state,
                'n_trials': (session_trials['state'] == state).sum()
            })

    return pd.DataFrame(rows)


def plot_response_counts(animal_id, from_session, to_session, stim, exp,
                        excluded_sessions, difficulties):
    """Plot response type counts across sessions.
    
    Creates a bar plot showing the number of Reward, Punish, and Abort
    outcomes across sessions. Includes total trials as a background bar.
    
    Args:
        animal_id (str): Animal identifier.
        from_session (int): Start session number (inclusive).
        to_session (int): End session number (inclusive).
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        excluded_sessions (list or set): Session numbers to exclude.
        difficulties (int or list): Difficulty level(s) to include.
        
    Returns:
        None: Displays plot using plt.show().
        
    Example:
        >>> plot_response_counts('mouse_1', 1, 20, stim, exp, set(), [1, 2])
    """
    response_counts = calculate_response_type(
        animal_id, from_session, to_session, stim, exp,
        excluded_sessions, difficulties
    )

    if response_counts.empty:
        print("🚫 No response data available for plotting.")
        return

    sessions = sorted(response_counts['session'].unique())
    session_map = {session: idx for idx, session in enumerate(sessions)}
    response_counts['session_idx'] = response_counts['session'].map(session_map)

    counts_wide = response_counts.pivot(
        index='session_idx',
        columns='state',
        values='n_trials'
    ).fillna(0)
    
    plt.figure(figsize=(max(8, len(sessions) * 1.2), 5))

    # Total trials background bar
    total_counts = (
        response_counts
        .groupby('session_idx', as_index=False)['n_trials']
        .sum()
    )

    plt.bar(
        total_counts['session_idx'],
        total_counts['n_trials'],
        width=0.85,
        color='gray',
        alpha=0.10,
        label='Total trials',
        zorder=1
    )

    x = counts_wide.index

    # Reward bar
    plt.bar(
        x - 0.18,
        counts_wide['Reward'],
        color="#36BF00",
        width=0.3,
        label='Reward',
        zorder=2
    )
    
    # Punish bar (stacked on top of Reward)
    plt.bar(
        x - 0.18,
        counts_wide['Punish'],
        bottom=counts_wide['Reward'],
        color="#FF0000",
        width=0.3,
        label='Punish',
        zorder=2
    )
    
    # Abort bar
    plt.bar(
        x + 0.18,
        counts_wide['Abort'],
        width=0.3,
        color="#000000",
        label='Abort',
        zorder=2
    )

    plt.xticks(
        ticks=range(len(sessions)),
        labels=sessions,
        rotation=80
    )

    plt.xlabel('Session', fontsize=18)
    plt.ylabel('Number of trials', fontsize=18)

    plt.title(
        f'Response counts across all trial modalities '
        f'(Animal: {animal_id}, Sessions: {from_session}-{to_session})',
        fontsize=18
    )

    plt.tick_params(axis='both', labelsize=12)

    plt.legend(
        title='Response',
        fontsize=12,
        title_fontsize=12
    )

    plt.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.show()