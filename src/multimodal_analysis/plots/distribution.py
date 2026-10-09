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

def get_condition_distribution_data(key, stim, exp, incl_aborts=False):
    """Fetch trial distribution data across conditions.
    
    Retrieves trial counts for each condition from the database for the 
    specified animal and session range.
    
    Args:
        key (dict): Analysis key with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session)
            - difficulties (list): Difficulty levels to include
            - excluded_sessions (set): Sessions to exclude
        stim: DataJoint stimuli schema
        exp: DataJoint experiments schema
        incl_aborts (bool): Include abort trials. Default is False.
        
    Returns:
        dict: Dictionary with keys 'animal_id', 'sessions', 'auditory', 
            'visual', 'multimodal', etc. Returns None if no valid data.
        
    Raises:
        ValueError: If animal_id not found in database.
    """
    animal_id = key['animal_id']
    from_s, to_s = key['sessions']
    excluded_sessions = key['excluded_sessions']
    difficulties = key['difficulties']
    
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
    
    for session in range(from_s, to_s + 1):
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


def plot_condition_trial_distribution(key, stim, exp, incl_aborts=False):
    """Plot trial counts across stimulus conditions.
    
    Creates a grouped bar plot showing the number of trials per condition
    for each session. Active conditions are displayed with separate bars.
    
    Args:
        key (dict): Analysis key with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session)
            - difficulties (list): Difficulty levels to include
            - excluded_sessions (set): Sessions to exclude
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        incl_aborts (bool, optional): Include abort trials. Defaults to False.
        
    Returns:
        matplotlib.axes.Axes: The axes object containing the plot.
        
    Example:
        >>> key = {'animal_id': 'mouse_1', 'sessions': (1, 20), ...}
        >>> ax = plot_condition_trial_distribution(key, stim, exp)
        >>> plt.show()
    """
    data = get_condition_distribution_data(key, stim, exp, incl_aborts)

    if data is None:
        return None

    animal_id = key['animal_id'] 
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


def plot_condition_distribution_percentage(key, stim, exp, incl_aborts=False):
    """Plot trial distribution as percentage across conditions.
    
    Creates a horizontal stacked bar chart showing the percentage of trials
    in each condition for each session.
    
    Args:
        key (dict): Analysis key with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session)
            - difficulties (list): Difficulty levels to include
            - excluded_sessions (set): Sessions to exclude
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        incl_aborts (bool, optional): Include abort trials. Defaults to False.
        
    Returns:
        None: Displays plot using matplotlib.
        
    Example:
        >>> key = {'animal_id': 'mouse_1', 'sessions': (1, 20), ...}
        >>> plot_condition_distribution_percentage(key, stim, exp)
    """
    data = get_condition_distribution_data(key, stim, exp, incl_aborts)

    if data is None:
        return

    animal_id = key['animal_id']
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

def get_object_distribution_data(
    key,
    stim,
    exp,
    incl_aborts=False,
):
    """Fetch visual and audiovisual trial counts per object and session.

    Visual trials have obj_mag > 0 and tone_volume = 0.
    Audiovisual trials have obj_mag > 0 and tone_volume > 0.

    Args:
        key (dict): Analysis configuration containing:
            - animal_id (int): Animal identifier.
            - sessions (tuple): Inclusive (from_session, to_session) range.
            - difficulties (list): Difficulty levels to include.
            - excluded_sessions (set): Sessions to exclude.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        incl_aborts (bool): Whether to include aborted trials.

    Returns:
        pandas.DataFrame: Trial counts with columns:
            - session: Session ID.
            - obj_id: Object identifier.
            - visual: Number of visual trials.
            - audiovisual: Number of audiovisual trials.
        Returns None if no valid data are found.
    """
    animal_id = key["animal_id"]
    from_s, to_s = key["sessions"]
    difficulties = key["difficulties"]
    excluded_sessions = set(key["excluded_sessions"])

    if difficulties is None or not difficulties:
        return None

    difficulty_filter = [
        {"difficulty": d}
        for d in difficulties
    ]

    difficulty = (
        exp.Condition.MatchPort()
        * exp.Trial()
    ).proj("difficulty")

    state_filter = (
        'state in ("Reward", "Punish", "Abort")'
        if incl_aborts
        else 'state in ("Reward", "Punish")'
    )

    # Find valid sessions for the selected animal.
    restr = exp.Session() & {"animal_id": animal_id}

    valid_sessions = set(
        (restr - exp.Session.Excluded).fetch("session")
    )

    records = []

    for session in range(from_s, to_s + 1):
        if session not in valid_sessions:
            continue

        if session in excluded_sessions:
            continue

        session_key = {
            "animal_id": animal_id,
            "session": session,
        }

        # Fetch trials with object magnitude and tone volume.
        trials = (
            stim.StimCondition.Trial
            * stim.Panda.Object.proj("obj_mag")
            * exp.Trial.StateOnset
            * difficulty
            * stim.Tones.proj("tone_volume")
            & difficulty_filter
            & session_key
            & state_filter
        ).fetch(format="frame").reset_index()

        if trials.empty:
            continue

        # Convert stimulus properties to numeric values.
        trials["obj_id"] = pd.to_numeric(
            trials["obj_id"],
            errors="coerce",
        )
        trials["obj_mag"] = pd.to_numeric(
            trials["obj_mag"],
            errors="coerce",
        )
        trials["tone_volume"] = pd.to_numeric(
            trials["tone_volume"],
            errors="coerce",
        )

        trials = trials.dropna(
            subset=["obj_id", "obj_mag", "tone_volume"]
        )

        # Keep only trials containing a visual object.
        trials = trials[trials["obj_mag"] > 0]

        if trials.empty:
            continue

        # VISUAL: obj_mag > 0 and tone_volume = 0.
        visual_trials = trials[
            trials["tone_volume"] == 0
        ]

        visual_counts = (
            visual_trials.groupby("obj_id")
            .size()
            .rename("visual")
        )

        # AUDIOVISUAL: obj_mag > 0 and tone_volume > 0.
        audiovisual_trials = trials[
            trials["tone_volume"] > 0
        ]

        audiovisual_counts = (
            audiovisual_trials.groupby("obj_id")
            .size()
            .rename("audiovisual")
        )

        # Combine counts for each object.
        counts = pd.concat(
            [visual_counts, audiovisual_counts],
            axis=1,
        ).fillna(0)

        if counts.empty:
            continue

        counts = counts.astype(int).reset_index()
        counts["session"] = session

        records.append(
            counts[
                ["session", "obj_id", "visual", "audiovisual"]
            ]
        )

    if not records:
        print("🚫 No valid object data")
        return None

    return (
        pd.concat(records, ignore_index=True)
        [["session", "obj_id", "visual", "audiovisual"]]
        .sort_values(["session", "obj_id"])
        .reset_index(drop=True)
    )


def get_object_distribution_trials(key, stim, exp, incl_aborts=False):
    """Return visual/audiovisual trial counts per object and session.

    Each object has one column containing 'visual / audiovisual' counts.
    Missing objects are represented as '0 / 0'.

    Args:
        key (dict): Analysis configuration.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiment schema.
        incl_aborts (bool): Whether to include aborted trials.

    Returns:
        pd.DataFrame: One row per session and one column per object.
    """
    data = get_object_distribution_data(
        key,
        stim,
        exp,
        incl_aborts=incl_aborts,
    )

    if data is None or data.empty:
        return pd.DataFrame(columns=["session"])

    # Pivot visual and audiovisual trial counts separately.
    visual = data.pivot_table(
        index="session",
        columns="obj_id",
        values="visual",
        aggfunc="sum",
        fill_value=0,
    )

    audiovisual = data.pivot_table(
        index="session",
        columns="obj_id",
        values="audiovisual",
        aggfunc="sum",
        fill_value=0,
    )

    # Ensure both tables contain the same object IDs.
    object_ids = sorted(
        set(visual.columns) | set(audiovisual.columns)
    )

    visual = visual.reindex(columns=object_ids, fill_value=0)
    audiovisual = audiovisual.reindex(columns=object_ids, fill_value=0)

    # Combine counts into one string per object.
    result = pd.DataFrame(index=visual.index)

    for obj_id in object_ids:
        result[f"obj{obj_id}"] = (
            visual[obj_id].astype(int).astype(str)
            + " / "
            + audiovisual[obj_id].astype(int).astype(str)
        )

    return (
        result.reset_index()
        .sort_values("session")
        .reset_index(drop=True)
    )

# def get_object_distribution_data(key, stim, exp, incl_aborts=False):
#     """Fetch the number of trials for each presented object per session.

#     Args:
#         key (dict): Analysis key with keys:
#             - animal_id (int): Animal identifier.
#             - sessions (tuple): (from_session, to_session).
#             - difficulties (list): Difficulty levels to include.
#             - excluded_sessions (set): Sessions to exclude.
#         stim: DataJoint stimuli schema.
#         exp: DataJoint experiments schema.
#         incl_aborts (bool): Include abort trials.

#     Returns:
#         pandas.DataFrame: Trial counts with columns:
#             - session
#             - obj_id
#             - n_trials
#         Returns None if no valid data are found.
#     """
#     animal_id = key["animal_id"]
#     from_s, to_s = key["sessions"]
#     difficulties = key["difficulties"]
#     excluded_sessions = key["excluded_sessions"]

#     if difficulties is None:
#         return None

#     difficulty_filter = [{"difficulty": d} for d in difficulties]

#     difficulty = (
#         exp.Condition.MatchPort()
#         * exp.Trial()
#     ).proj("difficulty")

#     state_filter = (
#         'state in ("Reward", "Punish", "Abort")'
#         if incl_aborts
#         else 'state in ("Reward", "Punish")'
#     )

#     # Find valid sessions for the selected animal.
#     restr = exp.Session() & {"animal_id": animal_id}
#     valid_sessions = (
#         restr - exp.Session.Excluded
#     ).fetch("session")

#     records = []

#     for session in range(from_s, to_s + 1):

#         if session not in valid_sessions:
#             continue

#         if session in excluded_sessions:
#             continue

#         session_key = {
#             "animal_id": animal_id,
#             "session": session,
#         }

#         trials = (
#             stim.StimCondition.Trial
#             * (stim.Panda.Object).proj("obj_mag")
#             * exp.Trial.StateOnset
#             * difficulty
#             & difficulty_filter
#             & session_key
#             & state_filter
#         ).fetch(format="frame").reset_index()

#         if trials.empty:
#             continue

#         # Keep only actual objects.
#         trials["obj_id"] = pd.to_numeric(
#             trials["obj_id"],
#             errors="coerce",
#         )

#         trials = trials.dropna(subset=["obj_id"])

#         if trials.empty:
#             continue

#         # Count trials for each object.
#         counts = (
#             trials.groupby("obj_id")
#             .size()
#             .reset_index(name="n_trials")
#         )

#         counts["session"] = session

#         records.append(counts)

#     if not records:
#         print("🚫 No valid object data")
#         return None

#     data = pd.concat(records, ignore_index=True)

#     return data[["session", "obj_id", "n_trials"]]


# def plot_object_distribution_object_trials(
#     key,
#     stim,
#     exp,
#     incl_aborts=False,
# ):
#     """Plot the number of trials for each object across sessions.

#     Each object has a consistent position and color across sessions.
#     Objects that were not presented in a session are not plotted.

#     Args:
#         key (dict): Analysis key.
#         stim: DataJoint stimuli schema.
#         exp: DataJoint experiments schema.
#         incl_aborts (bool): Include abort trials. Defaults to False.

#     Returns:
#         matplotlib.axes.Axes: The axes object containing the plot.
#     """
#     data = get_object_distribution_data(
#         key,
#         stim,
#         exp,
#         incl_aborts=incl_aborts,
#     )

#     if data is None:
#         return None

#     sessions = sorted(data["session"].unique())
#     object_ids = sorted(data["obj_id"].unique())

#     fig, ax = plt.subplots(
#         figsize=(12, 5),
#     )

#     x = np.arange(len(sessions))

#     # Consistent colors for objects across all sessions.
#     colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

#     n_objects = len(object_ids)
#     group_width = 0.8
#     width = group_width / n_objects

#     for object_idx, obj_id in enumerate(object_ids):

#         object_data = data[data["obj_id"] == obj_id]

#         values = []

#         for session in sessions:
#             match = object_data[
#                 object_data["session"] == session
#             ]

#             if match.empty:
#                 values.append(0)
#             else:
#                 values.append(
#                     match["n_trials"].iloc[0]
#                 )

#         offset = (
#             object_idx - (n_objects - 1) / 2
#         ) * width

#         ax.bar(
#             x + offset,
#             values,
#             width=width,
#             label=f"Object {int(obj_id)}",
#             color=colors[object_idx % len(colors)],
#         )

#     ax.set_xticks(x)
#     ax.set_xticklabels(sessions)

#     ax.set_xlabel("Session", fontsize=12)
#     ax.set_ylabel("Number of trials", fontsize=12)

    # animal_id = key["animal_id"]

    # title = (
    #     f"Object Trial Distribution "
    #     f"(Animal {animal_id}) - valid trials only"
    #     if not incl_aborts
    #     else
    #     f"Object Trial Distribution "
    #     f"(Animal {animal_id}) - valid + abort trials"
    # )

    # ax.set_title(title, fontsize=12)

    # ax.legend(
    #     bbox_to_anchor=(1.02, 1),
    #     loc="upper left",
    # )

    # ax.grid(
    #     axis="y",
    #     alpha=0.3,
    # )

    # plt.tight_layout()

    # return ax