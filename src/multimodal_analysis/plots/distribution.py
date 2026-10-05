"""
Trial distribution plotting functions.

This module contains functions for visualizing the distribution of trials
across different stimulus conditions and modalities.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from IPython.display import display
from ..utils.validators import validate_key, get_difficulties
from ..utils.queries import fetch_sessions


def get_condition_distribution_data(animal_id, from_session, to_session, stim, 
                                    exp, excluded_sessions, difficulties, 
                                    incl_aborts=False):
    """Fetch trial distribution data across conditions.
    
    Counts trials in each stimulus condition (auditory, visual, multimodal,
    difficult variants, etc.) for each session.
    
    Args:
        animal_id (str): Animal identifier.
        from_session (int): Start session number (inclusive).
        to_session (int): End session number (inclusive).
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        excluded_sessions (list or set): Session numbers to exclude.
        difficulties (int or list): Difficulty level(s) to include.
        incl_aborts (bool, optional): Include abort trials in state filter.
            Defaults to False (only Reward and Punish).
        
    Returns:
        dict or None: Dictionary with keys:
            - animal_id: Animal identifier
            - incl_aborts: Whether aborts were included
            - sessions: Array of session numbers
            - auditory: Array of auditory trial counts
            - visual: Array of visual trial counts
            - multimodal: Array of multimodal trial counts
            - multimodal_215: Array of multimodal object 215 counts
            - visual_215: Array of visual object 215 counts
            - multi_difficult: Array of multimodal difficult counts
            - visual_difficult: Array of visual difficult counts
            - no_stimulus: Array of no-stimulus trial counts
            
            Returns None if no valid data found.
            
    Example:
        >>> data = get_condition_distribution_data(
        ...     'mouse_1', 1, 20, stim, exp, set(), [1, 2], incl_aborts=False
        ... )
        >>> print(data['sessions'])
        >>> print(data['auditory'])
    """
    difficulties = get_difficulties({'difficulties': difficulties})
    
    if difficulties is None:
        return None

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')

    state_filter = (
        'state in ("Reward", "Punish", "Abort")'
        if incl_aborts
        else 'state in ("Reward", "Punish")'
    )
        
    restr = exp.Session() & {'animal_id': animal_id}
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')
    
    sessions = []
    auditory_counts = []
    visual_counts = []
    multimodal_counts = []
    multimodal_215_counts = []
    visual_215_counts = []
    multi_difficult_counts = []
    visual_difficult_counts = []
    no_stimulus_counts = []
    
    for session in range(from_session, to_session + 1):
        if session not in valid_sessions:
            continue
        
        if session in excluded_sessions:
            continue
    
        key = {'animal_id': animal_id, "session": session}
    
        # AUDITORY: tone_volume > 0 AND obj_mag == 0
        auditory_trials = (
            stim.StimCondition.Trial 
            * (stim.Panda.Object).proj('obj_mag') 
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & difficulty_filter
            & 'tone_volume > 0'
            & key
            & state_filter
        ).fetch(format='frame').reset_index()
        
        auditory_trials['obj_mag'] = pd.to_numeric(
            auditory_trials['obj_mag'], 
            errors='coerce'
        )
        auditory_trials = auditory_trials[auditory_trials['obj_mag'] == 0]
    
        # VISUAL: tone_volume = 0 AND obj_mag > 0 (non-difficult)
        visual_trials = (
            stim.StimCondition.Trial  
            * (stim.Panda.Object).proj('obj_mag') 
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume = 0'
            & key
            & difficulty_filter
            & 'obj_id NOT IN (214, 215, 217, 216)'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        visual_trials['obj_mag'] = pd.to_numeric(
            visual_trials['obj_mag'], 
            errors='coerce'
        )
        visual_trials = visual_trials[visual_trials['obj_mag'] > 0]

        # VISUAL DIFFICULT: tone_volume = 0 AND obj_mag > 0 (difficult)
        visual_difficult_trials = (
            stim.StimCondition.Trial  
            * (stim.Panda.Object).proj('obj_mag') 
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume = 0'
            & key
            & difficulty_filter
            & 'obj_id IN (214, 217, 216)'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        visual_difficult_trials['obj_mag'] = pd.to_numeric(
            visual_difficult_trials['obj_mag'], 
            errors='coerce'
        )
        visual_difficult_trials = visual_difficult_trials[
            visual_difficult_trials['obj_mag'] > 0
        ]

        # VISUAL 215: tone_volume = 0 AND obj_mag > 0 AND obj_id = 215
        visual215_trials = (
            stim.StimCondition.Trial  
            * (stim.Panda.Object).proj('obj_mag') 
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume = 0'
            & key
            & difficulty_filter
            & 'obj_id=215'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        visual215_trials['obj_mag'] = pd.to_numeric(
            visual215_trials['obj_mag'], 
            errors='coerce'
        )
        visual215_trials = visual215_trials[visual215_trials['obj_mag'] > 0]
    
        # MULTIMODAL: tone_volume > 0 AND obj_mag > 0 (non-difficult)
        multi_trials = (
            stim.StimCondition.Trial 
            * (stim.Panda.Object).proj('obj_mag') 
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'obj_id NOT IN (214, 215, 217, 216)'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        multi_trials['obj_mag'] = pd.to_numeric(
            multi_trials['obj_mag'], 
            errors='coerce'
        )
        multi_trials = multi_trials[multi_trials['obj_mag'] > 0]
    
        # MULTIMODAL 215: tone_volume > 0 AND obj_mag > 0 AND obj_id = 215
        multi215_trials = (
            stim.StimCondition.Trial 
            * (stim.Panda.Object).proj('obj_mag')  
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'obj_id=215'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        multi215_trials['obj_mag'] = pd.to_numeric(
            multi215_trials['obj_mag'], 
            errors='coerce'
        )
        multi215_trials = multi215_trials[multi215_trials['obj_mag'] > 0]

        # MULTIMODAL DIFFICULT: tone_volume > 0 AND obj_mag > 0 (difficult)
        multi_difficult_trials = (
            stim.StimCondition.Trial 
            * (stim.Panda.Object).proj('obj_mag')  
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'obj_id IN (214, 217, 216)'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        multi_difficult_trials['obj_mag'] = pd.to_numeric(
            multi_difficult_trials['obj_mag'], 
            errors='coerce'
        )
        multi_difficult_trials = multi_difficult_trials[
            multi_difficult_trials['obj_mag'] > 0
        ]

        # NO STIMULUS: tone_volume = 0 AND obj_mag = 0
        no_stimulus_trials = (
            stim.StimCondition.Trial 
            * (stim.Panda.Object).proj('obj_mag')  
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume = 0'
            & key
            & difficulty_filter
            & state_filter
        ).fetch(format='frame').reset_index()
        
        no_stimulus_trials['obj_mag'] = pd.to_numeric(
            no_stimulus_trials['obj_mag'], 
            errors='coerce'
        )
        no_stimulus_trials = no_stimulus_trials[
            no_stimulus_trials['obj_mag'] == 0
        ]
    
        auditory_trials = len(auditory_trials)
        visual_trials = len(visual_trials)
        multimodal_trials = len(multi_trials)
        visual215_trials = len(visual215_trials)
        multi215_trials = len(multi215_trials)
        multi_difficult_trials = len(multi_difficult_trials)
        visual_difficult_trials = len(visual_difficult_trials)
        no_stimulus_trials = len(no_stimulus_trials)

        sizes = np.array([
            auditory_trials, 
            visual_trials, 
            multimodal_trials, 
            multi215_trials, 
            visual215_trials, 
            multi_difficult_trials, 
            visual_difficult_trials, 
            no_stimulus_trials
        ])
        
        total = sizes.sum()
    
        if total == 0:
            continue
    
        sessions.append(session)
        auditory_counts.append(auditory_trials)
        visual_counts.append(visual_trials)
        multimodal_counts.append(multimodal_trials)
        multimodal_215_counts.append(multi215_trials)
        visual_215_counts.append(visual215_trials)
        multi_difficult_counts.append(multi_difficult_trials)
        visual_difficult_counts.append(visual_difficult_trials)
        no_stimulus_counts.append(no_stimulus_trials)

    if not sessions:
        print("🚫 No valid data")
        return None

    return {
        "animal_id": animal_id,
        "incl_aborts": incl_aborts,
        "sessions": np.array(sessions),
        "auditory": np.array(auditory_counts),
        "visual": np.array(visual_counts),
        "multimodal": np.array(multimodal_counts),
        "multimodal_215": np.array(multimodal_215_counts),
        "visual_215": np.array(visual_215_counts),
        "multi_difficult": np.array(multi_difficult_counts),
        "visual_difficult": np.array(visual_difficult_counts),
        "no_stimulus": np.array(no_stimulus_counts),
    }


def plot_condition_trial_distribution(animal_id, from_session, to_session, stim, 
                                     exp, excluded_sessions, difficulties, 
                                     incl_aborts=False):
    """Plot trial counts across stimulus conditions.
    
    Creates a grouped bar plot showing the number of trials per condition
    for each session. Active conditions are displayed with separate bars
    within each session.
    
    Args:
        animal_id (str): Animal identifier.
        from_session (int): Start session number (inclusive).
        to_session (int): End session number (inclusive).
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        excluded_sessions (list or set): Session numbers to exclude.
        difficulties (int or list): Difficulty level(s) to include.
        incl_aborts (bool, optional): Include abort trials. Defaults to False.
        
    Returns:
        matplotlib.axes.Axes: The axes object containing the plot.
        
    Example:
        >>> ax = plot_condition_trial_distribution(
        ...     'mouse_1', 1, 20, stim, exp, set(), [1, 2], incl_aborts=False
        ... )
        >>> plt.show()
    """
    data = get_condition_distribution_data(
        animal_id, from_session, to_session, stim, exp,
        excluded_sessions, difficulties, incl_aborts
    )

    if data is None:
        return None

    sessions = data["sessions"]

    conditions = {
        "Auditory": data["auditory"],
        "Visual": data["visual"],
        "Multimodal": data["multimodal"],
        "Visual 215": data["visual_215"],
        "Multimodal 215": data["multimodal_215"],
        "Visual difficult": data["visual_difficult"],
        "Multimodal difficult": data["multi_difficult"],
        "No stimulus": data["no_stimulus"],
    }

    fig, ax = plt.subplots(figsize=(12, 5))

    n_sessions = len(sessions)
    n_conditions = len(conditions)

    x = np.arange(n_sessions)
    group_width = 0.8
    
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    
    for session_idx in range(n_sessions):
    
        active = [
            (condition_idx, label, values[session_idx])
            for condition_idx, (label, values) in enumerate(conditions.items())
            if values[session_idx] > 0
        ]
    
        n_active = len(active)
    
        if n_active == 0:
            continue
    
        width = group_width / n_active
    
        for i, (condition_idx, label, value) in enumerate(active):
    
            offset = (i - (n_active - 1) / 2) * width
    
            ax.bar(
                x[session_idx] + offset,
                value,
                width=width,
                color=colors[condition_idx % len(colors)],
            )
    
    # Legend
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=colors[i % len(colors)])
        for i in range(len(conditions))
    ]
    
    ax.legend(
        handles,
        conditions.keys(),
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=True
    )

    ax.set_xticks(x)
    ax.set_xticklabels(sessions)
    ax.set_xlabel("Session", fontsize=12)
    ax.set_ylabel("Number of trials", fontsize=12)
    ax.set_title(f"Animal {data['animal_id']}", fontsize=12)

    plt.grid(alpha=0.3)
    plt.tight_layout()

    return ax


def plot_condition_distribution_percentage(animal_id, from_session, to_session, 
                                          stim, exp, excluded_sessions, 
                                          difficulties, incl_aborts=False):
    """Plot trial distribution as percentage across conditions.
    
    Creates a horizontal stacked bar chart showing the percentage of trials
    in each condition for each session.
    
    Args:
        animal_id (str): Animal identifier.
        from_session (int): Start session number (inclusive).
        to_session (int): End session number (inclusive).
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        excluded_sessions (list or set): Session numbers to exclude.
        difficulties (int or list): Difficulty level(s) to include.
        incl_aborts (bool, optional): Include abort trials. Defaults to False.
        
    Returns:
        None: Displays plot using plt.show().
        
    Example:
        >>> plot_condition_distribution_percentage(
        ...     'mouse_1', 1, 20, stim, exp, set(), [1, 2]
        ... )
    """
    data = get_condition_distribution_data(
        animal_id, from_session, to_session, stim, exp,
        excluded_sessions, difficulties, incl_aborts
    )

    if data is None:
        return

    sessions = data["sessions"]
    y = np.arange(len(sessions))
    
    plt.figure(figsize=(10, max(4, len(sessions) * 0.3)))
    
    condition_series = [
        ('Auditory', data["auditory"]),
        ('Visual', data["visual"]),
        ('Multimodal', data["multimodal"]),
        ('Multimodal_50/50', data["multimodal_215"]),
        ('Visual_50/50', data["visual_215"]),
        ('Visual_difficult', data["visual_difficult"]),
        ('Multimodal_difficult', data["multi_difficult"]),
        ('No Stimulus', data["no_stimulus"])
    ]

    left = np.zeros(len(sessions))

    for label, values in condition_series:
        if values.sum() == 0:
            continue

        # Convert to percentages
        percentages = []
        for i, session in enumerate(sessions):
            total = sum(v[i] for _, v in condition_series)
            pct = (values[i] / total * 100) if total > 0 else 0
            percentages.append(pct)
        percentages = np.array(percentages)

        plt.barh(
            y,
            percentages,
            left=left,
            label=label
        )

        left = left + percentages
    
    plt.yticks(y, sessions)   
    plt.xticks(range(0, 101, 5))
    
    plt.xlabel('Percentage', fontsize=12)
    plt.ylabel('Session ID', fontsize=12)
    plt.tick_params(axis='both', labelsize=12)
    
    title = (
        f'Trial Modality Distribution (Animal {animal_id}) - valids Only'
        if not incl_aborts
        else f'Trial Modality Distribution (Animal {animal_id}) - valids + aborts'
    )
    plt.title(title, fontsize=12)
    
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    
    plt.show()