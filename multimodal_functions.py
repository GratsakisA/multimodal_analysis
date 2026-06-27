import datajoint as dj
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from IPython.display import display, HTML

# ---------------- DATABASE CONFIG ----------------
dj.config['database.password'] = os.getenv('DJ_PASSWORD')
dj.config['database.host'] = 'database.eflab.org:3306'
dj.config["enable_python_native_blobs"] = True

schemata = {
    'exp': 'lab_experiments',
    'stim': 'lab_stimuli',
    'beh': 'lab_behavior',
    'inter': 'lab_interface',
    'rec': 'lab_recordings',
    'mice': 'lab_mice'
}

for schema, value in schemata.items():
    globals()[schema] = dj.create_virtual_module(schema, value, create_tables=True, create_schema=True)
    
# ---------------------------------------------------------------------------------------------------------

def get_condition_distribution(
    animal_id,
    from_session,
    to_session,
    stim,
    exp,
    manual_exclusion_sessions,
    difficulties,
    incl_aborts=False
):
    difficulties = _get_difficulties({'difficulties': difficulties})
    
    if difficulties is None:
        return

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
    
    auditory_pct = []
    visual_pct = []
    multimodal_pct = []
    multimodal_215_pct = []
    visual_215_pct = []

    
    for session in range(from_session, to_session + 1):
        if session not in valid_sessions:
            continue
        
        if session in manual_exclusion_sessions:
            continue
    
        key = {'animal_id': animal_id, "session":session}
    
        # auditory conditions = obj_mag = 0 & tone_volume > 0 ---------------------------------------------------------------
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
        
        auditory_trials['obj_mag'] = pd.to_numeric(auditory_trials['obj_mag'], errors='coerce')
        auditory_trials = auditory_trials[auditory_trials['obj_mag'] == 0]
    
        # visual conditions = obj_mag > 0 & tone_volume = 0 ---------------------------------------------------------------
        visual_trials = (
            stim.StimCondition.Trial  
            * (stim.Panda.Object).proj('obj_mag') 
            * exp.Trial.StateOnset 
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume = 0'
            & key
            & difficulty_filter
            & 'obj_id != 215'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        visual_trials['obj_mag'] = pd.to_numeric(visual_trials['obj_mag'], errors='coerce')
        visual_trials = visual_trials[visual_trials['obj_mag'] > 0]
    
        # multimodal conditions = obj_mag > 0 & tone_volume > 0 ---------------------------------------------------------------
        multi_trials = (
            stim.StimCondition.Trial 
            * (stim.Panda.Object).proj('obj_mag') 
            * exp.Trial.StateOnset
            * difficulty
            * (stim.Tones).proj('tone_volume') 
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'obj_id != 215'
            & state_filter
        ).fetch(format='frame').reset_index()
        
        multi_trials['obj_mag'] = pd.to_numeric(multi_trials['obj_mag'], errors='coerce')
        multi_trials = multi_trials[multi_trials['obj_mag'] > 0]
    
        # multimodal 50-50 conditions = obj_mag > 0 & tone_volume > 0 ---------------------------------------------------------------
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
        
        multi215_trials['obj_mag'] = pd.to_numeric(multi215_trials['obj_mag'], errors='coerce')
        multi215_trials = multi215_trials[multi215_trials['obj_mag'] > 0]
    
        # visual 50-50 conditions = obj_mag > 0 & tone_volume > 0 ---------------------------------------------------------------
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
        
        visual215_trials['obj_mag'] = pd.to_numeric(visual215_trials['obj_mag'], errors='coerce')
        visual215_trials = visual215_trials[visual215_trials['obj_mag'] > 0]
    
    
        # ---- replace with real per-session computation ----
        auditory_trials = len(auditory_trials)
        visual_trials = len(visual_trials)
        multimodal_trials = len(multi_trials)
        visual215_trials = len(visual215_trials)
        multi215_trials = len(multi215_trials)
    
        sizes = np.array([auditory_trials, visual_trials, multimodal_trials, multi215_trials, visual215_trials])
        total = sizes.sum()
    
        if total == 0:
            continue
    
        sessions.append(session)
        auditory_pct.append(sizes[0] / total * 100)
        visual_pct.append(sizes[1] / total * 100)
        multimodal_pct.append(sizes[2] / total * 100)
        multimodal_215_pct.append(sizes[3] / total * 100)
        visual_215_pct.append(sizes[4] / total * 100)

    if not sessions:
        print("🚫 No valid data for plotting")
        return
    
    # convert to numpy arrays (for alignment)
    auditory_pct = np.array(auditory_pct)
    visual_pct = np.array(visual_pct)
    multimodal_pct = np.array(multimodal_pct)
    multimodal_215_pct = np.array(multimodal_215_pct)
    visual_215_pct = np.array(visual_215_pct)
    
    y = np.arange(len(sessions))  
    
    plt.figure(figsize=(10, max(4, len(sessions) * 0.3)))
    
    condition_series = [
        ('Auditory', auditory_pct),
        ('Visual', visual_pct),
        ('Multimodal', multimodal_pct),
        ('Multimodal_50/50', multimodal_215_pct),
        ('Visual_50/50', visual_215_pct),
    ]

    left = np.zeros(len(sessions))

    for label, values in condition_series:
        if values.sum() == 0:
            continue

        plt.barh(
            y,
            values,
            left=left,
            label=label
        )

        left = left + values
    
    
    plt.yticks(y, sessions)   
    
    plt.xticks(range(0, 101, 5))
    
    plt.xlabel(
        'Percentage', 
        fontsize=12
    )
    
    plt.ylabel(
        'Session ID', 
        fontsize=12
    )
    
    plt.tick_params(
        axis='both', 
        labelsize=12
    )
    
    plt.title(
        f'Trial Modality Distribution (Animal {animal_id}) - valids Only' if not incl_aborts else f'Trial Modality Distribution (Animal {animal_id}) - valids + aborts', 
        fontsize=12
    )
    
    plt.legend(fontsize=12)
    
    plt.grid(alpha=0.3)
    
    plt.show()

def get_scatter_plot_modalities(
    animal_id,
    from_session,
    to_session,
    stim,
    exp,
    manual_exclusion_sessions,
    difficulties,
):
    difficulties = _get_difficulties({'difficulties': difficulties})
    if difficulties is None:
        return

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')
    
    restr = exp.Session() & {'animal_id': animal_id}
    
    valid_sessions = (
        restr - exp.Session.Excluded
    ).fetch('session')
    
    perf_per_condition = []
    skipped_sessions = []
    
    for session in range(from_session, to_session + 1):
        if session not in valid_sessions:
            continue

        if session in manual_exclusion_sessions:
            continue
    
        key = {'animal_id': animal_id, "session":session}
    
        # auditory conditions = obj_mag = 0 & tone_volume > 0
        auditory_trials = (
            stim.StimCondition.Trial * 
            (stim.Panda.Object).proj('obj_mag') * 
            exp.Trial.StateOnset * 
            difficulty *
            (stim.Tones).proj('tone_volume') 
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()
        
        auditory_trials['obj_mag'] = pd.to_numeric(auditory_trials['obj_mag'], errors='coerce')
        auditory_trials = auditory_trials[auditory_trials['obj_mag'] == 0]
    
        # visual conditions = obj_mag > 0 & tone_volume = 0
        visual_trials = (
            stim.StimCondition.Trial * 
            (stim.Panda.Object).proj('obj_mag') * 
            exp.Trial.StateOnset * 
            difficulty *
            (stim.Tones).proj('tone_volume') 
            & 'tone_volume = 0'
            & key
            & difficulty_filter
            & 'obj_id != 215'
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()
        
        visual_trials['obj_mag'] = pd.to_numeric(visual_trials['obj_mag'], errors='coerce')
        visual_trials = visual_trials[visual_trials['obj_mag'] > 0]
    
        # multimodal conditions = obj_mag > 0 & tone_volume > 0
        multi_trials = (
            stim.StimCondition.Trial * 
            (stim.Panda.Object).proj('obj_mag') * 
            exp.Trial.StateOnset * 
            difficulty *
            (stim.Tones).proj('tone_volume') 
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'obj_id != 215'
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()
        
        multi_trials['obj_mag'] = pd.to_numeric(multi_trials['obj_mag'], errors='coerce')
        multi_trials = multi_trials[multi_trials['obj_mag'] > 0]
    
        unimodal_trials = (
            stim.StimCondition.Trial *
            (stim.Panda.Object).proj('obj_mag') *
            exp.Trial.StateOnset *
            difficulty *
            (stim.Tones).proj('tone_volume')
            & key
            & difficulty_filter
            & 'obj_id != 215'
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()
        
        unimodal_trials['obj_mag'] = pd.to_numeric(
            unimodal_trials['obj_mag'],
            errors='coerce'
        )
        
        unimodal_trials['tone_volume'] = pd.to_numeric(
            unimodal_trials['tone_volume'],
            errors='coerce'
        )
        
        # apply the OR condition in pandas
        unimodal_trials = unimodal_trials[
            (
                (unimodal_trials['obj_mag'] > 0) &
                (unimodal_trials['tone_volume'] == 0)
            )
            |
            (
                (unimodal_trials['obj_mag'] == 0) &
                (unimodal_trials['tone_volume'] > 0)
            )
        ]
    
        # Skip sessions missing ANY modality
        if (
            len(auditory_trials) == 0 or
            len(visual_trials) == 0 or
            len(multi_trials) == 0
        ):
            skipped_sessions.append(session)
            continue
    
        # Calculate the performance in each condition
        visual_perf = round((visual_trials['state'] == 'Reward').mean(), 2)
        auditory_perf = round((auditory_trials['state'] == 'Reward').mean(), 2)
        multi_perf = round((multi_trials['state'] == 'Reward').mean(), 2)
        uni_perf = round((unimodal_trials['state'] == 'Reward').mean(), 2)
    
        perf_per_condition.append({
            'session': session,
            'auditory_perf': auditory_perf,
            'visual_perf': visual_perf,
            'multi_perf': multi_perf,
            'uni_perf': uni_perf,
        })

        
        
    perf_per_condition = pd.DataFrame(perf_per_condition)


    if perf_per_condition.empty:
        print('🚫 No valid data for plotting')
        return
            
    perf_per_condition['session'] = perf_per_condition['session'].astype(str)
    
    # plotting =======================
    fig, axes = plt.subplots(1, 4, figsize=(15, 5), sharex=True, sharey=False)
    
    # Auditory vs Visual
    sns.scatterplot(
        data=perf_per_condition,
        x='auditory_perf',
        y='visual_perf',
        ax=axes[0],
        hue='session',
        s=40
    )
    axes[0].set_title('Auditory vs Visual', fontsize=12)
    axes[0].set_ylabel('visual_perf', fontsize=12)
    axes[0].set_xlabel('auditory_perf', fontsize=12)
    axes[0].tick_params(axis='both', labelsize=12)
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1.1)
    axes[0].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    # Visual vs Multimodal
    sns.scatterplot(
        data=perf_per_condition,
        x='visual_perf',
        y='multi_perf',
        ax=axes[1],
        hue='session',
        s=40,
        legend=False
    )
    axes[1].set_title('Visual vs Multimodal', fontsize=12)
    axes[1].set_ylabel('multimodals_perf', fontsize=12)
    axes[1].set_xlabel('visual_perf', fontsize=12)
    axes[1].tick_params(axis='both', labelsize=12)
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    # Auditory vs Multimodal
    sns.scatterplot(
        data=perf_per_condition,
        x='auditory_perf',
        y='multi_perf',
        ax=axes[2],
        hue='session',
        s=40,
        legend=False
    )
    axes[2].set_title('Auditory vs Multimodal', fontsize=12)
    axes[2].set_ylabel('multimodals_perf', fontsize=12)
    axes[2].set_xlabel('auditory_perf', fontsize=12)
    axes[2].tick_params(axis='both', labelsize=12)
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1.1)
    axes[2].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    # Unimodals vs Multimodal
    sns.scatterplot(
        data=perf_per_condition,
        x='uni_perf',
        y='multi_perf',
        ax=axes[3],
        hue='session',
        s=40,
        legend=False
    )
    axes[3].set_title('Unimodals vs Multimodals', fontsize=12)
    axes[3].set_ylabel('multimodals_perf', fontsize=12)
    axes[3].set_xlabel('unimodals_perf', fontsize=12)
    axes[3].tick_params(axis='both', labelsize=12)
    axes[3].set_xlim(0, 1)
    axes[3].set_ylim(0, 1.1)
    axes[3].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    plt.suptitle(f'Performance Across Auditory, Visual, and Multimodal Conditions (Animal {animal_id})')
    
    plt.tight_layout()
    plt.show()
    
    
    
    print("Skipped sessions (missing one or more modalities):", skipped_sessions)
    display(perf_per_condition)


DEFAULT_OBJECT_IDS = [211, 212, 213, 214, 215, 216, 217, 218, 219]
OBJECT_ALIASES = {211: [211, 1], 219: [219, 2]}

# ---------------- INTERNAL FUNCTIONS ----------------
def _validate_key(key):
    required = ['animal_id', 'sessions']
    for r in required:
        if r not in key:
            raise KeyError(f"Missing required key: '{r}'")

def _get_difficulties(key):
    difficulties = key.get('difficulties')

    if difficulties is None or (
        hasattr(difficulties, '__len__') and len(difficulties) == 0
    ):
        print("complete the difficulty level")
        return None

    if isinstance(difficulties, (int, float)):
        return [difficulties]

    return difficulties


def _fetch_sessions(animal_id, session_range):
    from_s, to_s = session_range

    restr = (
        exp.Session()
        & {'animal_id': animal_id}
        & f'session >= {from_s}'
        & f'session <= {to_s}'
    )

    return (restr - exp.Session.Excluded).fetch('session')


# ----- unimodal visual trials -----
def _process_object(animal_id, obj_id, sessions, difficulties, excluded_sessions):
    
    rows = []
    
    difficulty_filter = [{'difficulty': d} for d in difficulties]

    for session in sessions:
        
        if session in excluded_sessions:
            continue
            
        key_session = {'animal_id': animal_id, 'session': session}

        session_date = (exp.Session() & key_session).fetch1('session_tmst').strftime('%Y-%m-%d')
        
        obj_ids = OBJECT_ALIASES.get(obj_id, [obj_id])
        
        obj_query = ' OR '.join([f'obj_id={o}' for o in obj_ids])
        
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
            ).fetch(
                'session', 
                'trial_idx', 
                as_dict=True
            )
        )
        
        if visual_trials.empty:
            continue
            
        visual_keys = visual_trials.to_dict('records')
        
        state_visual = pd.DataFrame(
            (
                exp.Trial.StateOnset 
                & key_session 
                & visual_keys
            ).fetch(
                'state', 
                as_dict=True
            )
        )
        
        total_trials = len(exp.Trial & key_session)
        
        rew = (state_visual['state'] == 'Reward').sum()
        pun = (state_visual['state'] == 'Punish').sum()
        
        valid = rew + pun
        
        performance = round(rew / valid, 2) if valid else 0
        
        rows.append(
            {
                'animal_id': animal_id,
                'session': session,
                'date': session_date,
                'session_trials': total_trials,
                'valid_obj_trials': valid,
                'performance': performance,
                'reward': rew,
                'punish': pun,
                'abort': (state_visual['state'] == 'Abort').sum()
        }
                   )
    return pd.DataFrame(rows)

def fetch_visual_data(key):
    """
    Fetch object-wise visual performance DataFrames (without displaying them).
    Returns a dict {object_id: df}, excluding objects with no trials.
    """
    _validate_key(key)
    
    animal_id = key['animal_id']

    difficulties = _get_difficulties(key)
    if difficulties is None:
        return {}
    
    object_ids = key.get('object_ids', DEFAULT_OBJECT_IDS)
    
    excluded_sessions = key.get(
        'excluded_sessions', 
        set()
    )
    
    sessions = _fetch_sessions(
        animal_id=animal_id,
        session_range=key.get('sessions')
    )

    object_dfs = {}
    
    for obj_id in object_ids:
        df = _process_object(
            animal_id=animal_id,
            obj_id=obj_id,
            sessions=sessions,
            difficulties=difficulties,
            excluded_sessions=excluded_sessions
        )
        
        if not df.empty:
            object_dfs[obj_id] = df
            
    return object_dfs


def get_visual_performance_summary(key):
    """
    Fetch and display object-wise DataFrames in Jupyter.
    """
    object_dfs = fetch_visual_data(key)

    if not object_dfs:
        print("🚫 No valid visual data to analysis.")
        return object_dfs
    
    display(HTML("<h2><b>Unimodal visual trials</b></h2>"))    
    
    for obj_id, df in object_dfs.items():
        print(f"Object {obj_id}:")
        display(df)
        
    return object_dfs


def plot_visual_performance_per_object(
    key,
    criterion=0.65
):
    """
    Fetch data and plot performance (line + bar) only, no DataFrame display.
    """
    animal_id = key['animal_id']
    
    difficulties = key['difficulties'] 
    
    object_dfs = fetch_visual_data(key)  # fetch silently
    
    row_data = []
    
    for obj_id, df in object_dfs.items():
        if not df.empty:
            df['object'] = str(obj_id)
            row_data.append(
                df[[
                    'session', 
                    'object', 
                    'performance', 
                    'reward', 
                    'punish', 
                    'abort', 
                    'valid_obj_trials'
                ]]
            )
        else:
            print(
                f"🫠 Skipped file for object {obj_id}. Empty or malformed."
            )
    if not row_data:
        print(
            "🚫 No valid visual data to plot."
        )
        return

    row_data = pd.concat(row_data, ignore_index=True)
    
    row_data['session'] = row_data['session'].astype(str)
    
    # Make session numeric
    row_data['session'] = pd.to_numeric(row_data['session'])

    # Get session range from key
    if key.get('sessions'):
        from_s, to_s = key['sessions']
    else:
        from_s = row_data['session'].min()
        to_s = row_data['session'].max()

    sessions = sorted(row_data["session"].unique())
    
    session_map = {s: i for i, s in enumerate(sessions)}
    
    row_data["session_idx"] = row_data["session"].map(session_map)

    # Line plot -------------------------------
    fig, axes = plt.subplots(1, 2, 
                             figsize=(18, 5), # figure size
                             constrained_layout=True)
    sns.lineplot(
        data=row_data, 
        x='session_idx', 
        y='performance', 
        hue='object', 
        marker='o', 
        ax=axes[0]
    )
    
    axes[0].set_title(
        f"Visual performance across sessions",
        fontsize=18
    )

    axes[0].set_xlabel(
        'Session idx',
        fontsize=18
    )

    
    axes[0].set_ylabel(
        'Performance',
        fontsize=18
    )
    
    axes[0].set_ylim(0, 1.1)
    
    axes[0].grid(alpha=0.2)

    # horizontal line for chance level in unimodal-visual trials
    axes[0].axhline(
        y=0.5, 
        color='grey', 
        linestyle='--', 
        alpha=0.3, 
        label='chance'
    )

    # horizontal line for criterion in unimodal-visual trials
    axes[0].axhline(
        criterion, 
        color='g', 
        linestyle='--', 
        alpha=0.3, 
        label=f'criterion ({criterion:.0%})'
    )
    
    axes[0].tick_params(
        axis='both', 
        labelsize=16
    )
    
    axes[0].set_axisbelow(True)
    
    axes[0].legend(
        fontsize=8
    )
    
    axes[0].set_xticks(range(len(sessions)))

    axes[0].set_xticklabels(
        sessions, 
        rotation=80
    )


    # Bar plot ------------------------------------------
    performance_summary = row_data.groupby('object')[['reward', 'punish']].sum().reset_index()
    performance_summary['mean_performance'] = round(
        performance_summary['reward'] / (
            performance_summary['reward'] + performance_summary['punish']), 2)
    
    sns.barplot(
        data=row_data,
        x='object',
        y='performance',
        hue='object',
        errorbar=('ci', 95),
        ax=axes[1]
    )
    
    axes[1].set_title(
        f'Mean visual performance per object (± 95% CI)', 
        fontsize=18
    )
    axes[1].set_ylabel(
        'Mean performance',
        fontsize=18
    )
    
    axes[1].set_xlabel(
        'Object ids',
        fontsize=18
    )

    axes[1].tick_params(
        axis='both', 
        labelsize=16
    )
    
    axes[1].set_ylim(0, 1.1)
    
    axes[1].grid(axis='y', alpha=0.2)
    
    axes[1].axhline(
        y=0.5, 
        color='grey', 
        linestyle='--', 
        alpha=0.3
    ) 
    
    axes[1].axhline(
        criterion, 
        color='green', 
        linestyle='--', 
        alpha=0.3,
        label=f'criterion ({criterion:.0%})'
    ) 
    
    axes[1].set_axisbelow(True)
    
    # Remove redundant legend on bar plot
    axes[1].get_legend()
    
    # ---------------------------------------------------------------
    # add text inside the bars for n_sessions and n_total_trials
    # Sum of valid trials per object
    total_trials_per_object = row_data.groupby('object')['valid_obj_trials'].sum()
    
    for i, obj in enumerate(row_data['object'].unique()):
        n_sessions = row_data[row_data['object'] == obj].shape[0] # Number of sessions
        n_trials = total_trials_per_object[obj] # Total valid trials
        bar_height = row_data[row_data['object'] == obj]['performance'].mean()  # Mean bar height for this object
        axes[1].text(i, 
                     0.05,
                     f'sessions={n_sessions}\ntrials={n_trials}',
                     ha='center',
                     fontsize=10, 
                     color='black', 
                     bbox=dict(facecolor='white', #  the box behind the text is white
                               edgecolor='none', # no border around the box
                               alpha=0.5, # transparency
                               pad=5) # small padding around the text
    )
        
    plt.suptitle(
        f"Performance in unimodal $\\mathbf{{visual}}$ trials for each object (animal: {animal_id}, sessions: {from_s}-{to_s})"
    )
    
    plt.show()


# --------------- multimodal trials ---------------
def _process_multimodal_object(
    animal_id,
    obj_id,
    sessions,
    difficulties,
    excluded_sessions
):
    rows = []

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')

    for session in sessions:

        if session in excluded_sessions:
            continue

        key_session = {
            'animal_id': animal_id,
            'session': session
        }
        
        session_date = (exp.Session() & key_session).fetch1('session_tmst').strftime('%Y-%m-%d')

        obj_ids = OBJECT_ALIASES.get(obj_id, [obj_id])
        obj_query = ' OR '.join([f'obj_id={o}' for o in obj_ids])

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
            ).fetch(
                as_dict=True
            )
        )

        if multi_trials.empty:
            continue

        multi_trials['obj_mag'] = pd.to_numeric(
            multi_trials['obj_mag'],
            errors='coerce'
        )

        multi_trials = multi_trials[
            multi_trials['obj_mag'] > 0
        ]

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

        rows.append(
            {
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
            }
        )

    return pd.DataFrame(rows)

def fetch_multimodal_data(key):
    """
    Fetch object-wise multimodal performance DataFrames.
    Returns:
        {object_id: dataframe}
    """

    _validate_key(key)

    animal_id = key['animal_id']

    difficulties = _get_difficulties(key)
    if difficulties is None:
        return {}

    

    object_ids = key.get('object_ids', DEFAULT_OBJECT_IDS)

    excluded_sessions = key.get(
        'excluded_sessions',
        set()
    )

    sessions = _fetch_sessions(
        animal_id=animal_id,
        session_range=key.get('sessions')
    )

    object_dfs = {}

    for obj_id in object_ids:

        df = _process_multimodal_object(
            animal_id=animal_id,
            obj_id=obj_id,
            sessions=sessions,
            difficulties=difficulties,
            excluded_sessions=excluded_sessions
        )

        if not df.empty:
            object_dfs[obj_id] = df

    return object_dfs

def get_multimodal_performance_summary(key):

    object_dfs = fetch_multimodal_data(key)

    if not object_dfs:
        print("🚫 No valid multimodal data for analysis")
        return object_dfs

    display(HTML("<h2><b>Multimodal trials</b></h2>"))

    for obj_id, df in object_dfs.items():

        print(f"Object {obj_id}:")
        display(df)

    return object_dfs

def plot_multimodal_performance_per_object(
    key,
    criterion=0.65
):

    animal_id = key['animal_id']

    object_dfs = fetch_multimodal_data(key)

    row_data = []

    for obj_id, df in object_dfs.items():

        if not df.empty:

            df = df.copy()
            df['object'] = str(obj_id)

            row_data.append(
                df[
                    [
                        'session',
                        'object',
                        'performance',
                        'reward',
                        'punish',
                        'abort',
                        'valid_obj_trials'
                    ]
                ]
            )

    if not row_data:
        print("🚫 No valid multimodal data to plot")
        return

    row_data = pd.concat(row_data, ignore_index=True)

    row_data['session'] = pd.to_numeric(
        row_data['session']
    )
    
    
    sessions_all = sorted(row_data['session'].unique())
    

    objects_all = row_data['object'].unique()

    full_index = pd.MultiIndex.from_product(
        [sessions_all, objects_all],
        names=['session', 'object']
    )

    df_full = (
        row_data
        .set_index(['session', 'object'])
        .reindex(full_index)
        .reset_index()
    )


    # map sessions -> continuous index (0,1,2,3,...)
    session_map = {s: i for i, s in enumerate(sorted(df_full["session"].unique()))}
    df_full["session_idx"] = df_full["session"].map(session_map)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(18, 5),
        constrained_layout=True
    )

    # ---------------- LINE PLOT ----------------

    sns.lineplot(
        data=df_full,
        x='session_idx',
        y='performance',
        hue='object',
        marker='o',
        ax=axes[0]
    )

    sessions = sorted(df_full["session"].unique())

    axes[0].set_xticks(range(len(session_map)))
    axes[0].set_xticklabels(sorted(session_map.keys()), rotation=80)
    
    axes[0].set_title(
        'Multimodal performance across sessions',
        fontsize=18
    )

    axes[0].set_xlabel(
        'Session idx',
        fontsize=18
    )

    axes[0].set_ylabel(
        'Performance',
        fontsize=18
    )

    axes[0].tick_params(
        axis='both', 
        labelsize=16
    )

    axes[0].set_ylim(0, 1.1)

    axes[0].axhline(
        0.5,
        color='grey',
        linestyle='--',
        alpha=0.3,
        label='chance'
    )

    axes[0].axhline(
        criterion,
        color='g',
        linestyle='--',
        alpha=0.3,
        label=f'criterion ({criterion:.0%})'
    )

    axes[0].legend(
        fontsize=8
    )

    axes[0].grid(alpha=0.2)

    # ---------------- BAR PLOT ----------------

    sns.barplot(
        data=row_data,
        x='object',
        y='performance',
        hue='object',
        errorbar=('ci', 95),
        ax=axes[1]
    )

    axes[1].set_title(
        'Mean multimodal performance (±95% CI)',
        fontsize=18
    )

    axes[1].set_xlabel(
        'Object ids',
        fontsize=18
    )

    axes[1].set_ylabel(
        'Mean performance',
        fontsize=18
    )

    
    axes[1].set_ylim(0, 1.1)

    axes[1].axhline(
        0.5,
        color='grey',
        linestyle='--',
        alpha=0.3,
        label='chance'
    )

    axes[1].tick_params(
        axis='both', 
        labelsize=16
    )


    axes[1].axhline(
        criterion,
        color='green',
        linestyle='--',
        alpha=0.3,
        label=f'criterion ({criterion:.0%})'
    )

    total_trials_per_object = (
        row_data
        .groupby('object')['valid_obj_trials']
        .sum()
    )

    for i, obj in enumerate(
        row_data['object'].unique()
    ):

        n_sessions = (
            row_data[row_data['object'] == obj]
            .shape[0]
        )

        n_trials = total_trials_per_object[obj]

        axes[1].text(
            i,
            0.05,
            f'sessions={n_sessions}\ntrials={n_trials}',
            ha='center',
            fontsize=9,
            bbox=dict(
                facecolor='white',
                edgecolor='none',
                alpha=0.5
            )
        )

    if key.get('sessions'):
        from_s, to_s = key['sessions']
        session_text = f"{from_s}-{to_s}"
    else:
        session_text = "selected range"

    plt.suptitle(
        f"Performance in $\\mathbf{{multimodal}}$ trials for each object (animal: {animal_id}, sessions: {session_text})"
    )

    plt.show()

# Performance in unimodal-auditory trials 
def compute_auditory_performance_summary(key):
    animal_id = key['animal_id']
    from_session, to_session = key['sessions']
    
    difficulties = _get_difficulties(key)
    if difficulties is None:
        return pd.DataFrame(), pd.DataFrame()
    
    manual_exclusion_sessions = key.get('excluded_sessions', [])
    
    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')
    
    restr = exp.Session() & {'animal_id': animal_id}
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')
    
    rows_pulse0 = []
    rows_pulse100 = []
    
    for session in range(from_session,to_session + 1):
    
        if session not in valid_sessions:
                continue

        if session in manual_exclusion_sessions:
                continue
    
        key_session = {'animal_id': animal_id, 'session': session}
    
        session_date = (
            exp.Session() & key_session).fetch1('session_tmst').strftime('%Y-%m-%d')
    
        auditory_trials = (
            stim.StimCondition.Trial *
            (stim.Panda.Object).proj('obj_mag') *
            exp.Trial.StateOnset *
            difficulty *
            (stim.Tones).proj('tone_volume', 'tone_pulse_freq')
            & 'tone_volume > 0'
            & key_session
            & difficulty_filter
            & 'state in ("Reward", "Punish", "Abort")'
        ).fetch(format='frame').reset_index()
    
        auditory_trials['obj_mag'] = pd.to_numeric(auditory_trials['obj_mag'], errors='coerce')
        auditory_trials = auditory_trials[auditory_trials['obj_mag'] == 0]
    
        pulse0 = auditory_trials[auditory_trials['tone_pulse_freq'] == 0]
        pulse100 = auditory_trials[auditory_trials['tone_pulse_freq'] == 100]
    
        for df_trials, rows in [(pulse0, rows_pulse0), (pulse100, rows_pulse100)]:

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
                'tone_pulse_freq': 0 if df_trials is pulse0 else 100
            })

    pulse0_df = pd.DataFrame(rows_pulse0)
    pulse100_df = pd.DataFrame(rows_pulse100)

    return pulse0_df, pulse100_df

def get_auditory_performance_summary(
    key, 
    pulse_freq='all'
):
  
    pulse0_df, pulse100_df = compute_auditory_performance_summary(key)

    if pulse0_df.empty and pulse100_df.empty:
        print("🚫 No valid auditory data for analysis")
        return pulse0_df, pulse100_df

    display(HTML("<h2><b>Unimodal auditory trials</b></h2>"))
    
    if pulse_freq == 'all':
        display(HTML('<b><h4>Pulsed tone</b> (<i>tone_pulse_freq = 100 Hz</i>)</h4>'))
        display(pulse100_df)
    
        display(HTML('<b><h4>Continuous tone</b> (<i>tone_pulse_freq = 0 Hz</i>)</h4>'))
        display(pulse0_df)

    elif pulse_freq == 0:
        display(HTML('<b><h4>Continuous tone</b> (<i>tone_pulse_freq = 0 Hz</i>)</h4>'))
        display(pulse0_df)
    
    elif pulse_freq == 100:
        display(HTML('<b><h4>Pulsed tone</b> (<i>tone_pulse_freq = 100 Hz</i>)</h4>'))
        display(pulse100_df)
        
    else:
        raise ValueError("pulse_freq must be 'all', 0, or 100")

    return pulse0_df, pulse100_df


def plot_auditory_performance_per_object(
    key, 
    criterion=0.65
):
    animal_id = key['animal_id']
    from_s, to_s = key['sessions']
    
    # get data internally
    pulse0_df, pulse100_df = compute_auditory_performance_summary(key)

    if pulse0_df.empty and pulse100_df.empty:
        print("🚫 No valid auditory data to plot")
        return

    df_all = pd.concat(
        [pulse0_df, pulse100_df],
        ignore_index=True
    ).sort_values(['tone_pulse_freq', 'session'])

    sessions_all = sorted(df_all['session'].unique())
    session_map = {s: i for i, s in enumerate(sessions_all)}
    
    df_all['session_idx'] = df_all['session'].map(session_map)

    fig, axes = plt.subplots(1, 2, 
                             figsize=(18, 5), # figure size
                             constrained_layout=True)
    

    # Line plot 
    for freq in [0, 100]:
        df_sub = df_all[df_all['tone_pulse_freq'] == freq]

        axes[0].plot(
            df_sub['session_idx'],
            df_sub['performance'],
            marker='o',
            label=f'{freq} Hz'
        )

    axes[0].set_title(
        'Auditory performance across sessions', 
        fontsize=18
    )

    axes[0].set_xticks(range(len(sessions_all)))
    axes[0].set_xticklabels(sessions_all, rotation=80)

    axes[0].tick_params(
        axis='both', 
        labelsize=16
    )
    
    axes[0].set_xlabel(
        'Session idx', 
        fontsize=18
    )
    
    axes[0].set_ylabel(
        'Performance', 
        fontsize=18
    )
    
    axes[0].set_ylim(0, 1.1)

    axes[0].axhline(
        0.5, 
        color='grey', 
        linestyle='--', 
        alpha=0.3, 
        label='chance'
    )
    
    axes[0].axhline(
        criterion, 
        color='green', 
        linestyle='--', 
        alpha=0.3,
        label=f'criterion ({criterion:.0%})'
    )

    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    # Bar plot 
    palette = {0: 'blue', 100: 'orange'}

    sns.barplot(
        data=df_all,
        x='tone_pulse_freq',
        y='performance',
        hue='tone_pulse_freq',
        palette=palette,
        errorbar=('ci', 95),
        ax=axes[1]
    )

    axes[1].set_xticks([0, 1])

    axes[1].tick_params(
        axis='both', 
        labelsize=16
    )
    
    axes[1].set_xticklabels(
        ['0 Hz', '100 Hz'], 
        fontsize=16
    )

    axes[1].set_title('Mean auditory performance (±95% CI)', fontsize=18)
    axes[1].set_xlabel('Tone pulse frequency (Hz)', fontsize=18)
    axes[1].set_ylabel('Mean performance', fontsize=18)
    axes[1].set_ylim(0, 1.1)

    axes[1].axhline(0.5, color='grey', linestyle='--', alpha=0.3)
    axes[1].axhline(criterion, color='green', linestyle='--', alpha=0.3)

    axes[1].legend_.remove() if axes[1].get_legend() else None


    plt.suptitle(
        f"Performance in unimodal $\\mathbf{{auditory}}$ trials for each tone frequency "
        f"(Animal {animal_id}, sessions: {from_s}-{to_s})"
    )
    plt.show()

def compute_modality_performance(
    animal_id,
    from_session,
    to_session,
    stim,
    exp,
    manual_exclusion_sessions,
    difficulties,
):
    difficulties = _get_difficulties({'difficulties': difficulties})
    if difficulties is None:
        return pd.DataFrame()

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')

    restr = exp.Session() & {'animal_id': animal_id}
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')

    perf_per_condition = []

    for session in range(from_session, to_session + 1):

        if session not in valid_sessions or session in manual_exclusion_sessions:
            continue

        key = {'animal_id': animal_id, "session": session}

        auditory_stateonset = (
            stim.StimCondition.Trial *
            (stim.Panda.Object).proj('obj_mag') *
            exp.Trial.StateOnset *
            difficulty *
            (stim.Tones).proj('tone_volume')
            & 'tone_volume > 0'
            & key
            & difficulty_filter
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()

        auditory_stateonset['obj_mag'] = pd.to_numeric(auditory_stateonset['obj_mag'], errors='coerce')
        auditory_stateonset = auditory_stateonset[auditory_stateonset['obj_mag'] == 0]

        visual_stateonset = (
            stim.StimCondition.Trial *
            (stim.Panda.Object).proj('obj_mag') *
            exp.Trial.StateOnset *
            difficulty *
            (stim.Tones).proj('tone_volume')
            & 'tone_volume = 0'
            & key
            & 'obj_id != 215'
            & difficulty_filter
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()

        visual_stateonset['obj_mag'] = pd.to_numeric(visual_stateonset['obj_mag'], errors='coerce')
        visual_stateonset = visual_stateonset[visual_stateonset['obj_mag'] > 0]

        multi_stateonset = (
            stim.StimCondition.Trial *
            (stim.Panda.Object).proj('obj_mag') *
            exp.Trial.StateOnset *
            difficulty *
            (stim.Tones).proj('tone_volume')
            & 'tone_volume > 0'
            & key
            & 'obj_id != 215'
            & difficulty_filter
            & 'state in ("Reward", "Punish")'
        ).fetch(format='frame').reset_index()

        multi_stateonset['obj_mag'] = pd.to_numeric(multi_stateonset['obj_mag'], errors='coerce')
        multi_stateonset = multi_stateonset[multi_stateonset['obj_mag'] > 0]

        if len(auditory_stateonset) == 0 or len(visual_stateonset) == 0 or len(multi_stateonset) == 0:
            continue

        perf_per_condition.append({
            'session': session,
            'auditory_perf': round((auditory_stateonset['state'] == 'Reward').mean(),2),
            'visual_perf': round((visual_stateonset['state'] == 'Reward').mean(), 2),
            'multi_perf': round((multi_stateonset['state'] == 'Reward').mean(), 2),
        })

    return pd.DataFrame(perf_per_condition)

def get_linePlot_per_modality_across_sessions(
    animal_id,
    from_session,
    to_session,
    stim,
    exp,
    manual_exclusion_sessions,
    difficulties,
    criterion=0.65
):
    perf_per_modality = compute_modality_performance(
        animal_id,
        from_session,
        to_session,
        stim,
        exp,
        manual_exclusion_sessions,
        difficulties
    )

    if perf_per_modality.empty:
        print(" 🚫 No data available for plotting.")
        return

    perf_per_modality = perf_per_modality.sort_values('session').copy()
    sessions = perf_per_modality['session'].tolist()
    perf_per_modality['session_idx'] = range(len(perf_per_modality))

    plt.figure(figsize=(max(8, len(sessions) * 1.2), 5))

    sns.lineplot(
        data=perf_per_modality, 
        x='session_idx', 
        y='auditory_perf', 
        marker='o', 
        label='Auditory'
        )
    
    sns.lineplot(
        data=perf_per_modality, 
        x='session_idx', 
        y='visual_perf', 
        marker='o', 
        label='Visual')
    
    sns.lineplot(
        data=perf_per_modality, 
        x='session_idx', 
        y='multi_perf', 
        marker='o', 
        label='Multimodal'
        )
    
    plt.title(
        f'Performance across sessions in each modality\n(Animal: {animal_id}, Sessions: {from_session}-{to_session})',
        fontsize=18
        )
    
    plt.xlabel(
        'Session idx', 
        fontsize=18
        )
    
    plt.ylabel(
        'Performance', 
        fontsize=18
        )

    plt.xticks(
        ticks=range(len(sessions)),
        labels=sessions,
        rotation=80
    )
    
    plt.ylim(0, 1.1)
    
    plt.tick_params(
        axis='both', 
        labelsize=16
    )

    plt.axhline(
        0.5, 
        color='grey', 
        linestyle='--', 
        alpha=0.3, 
        label='chance'
    )

    plt.axhline(
        criterion, 
        color='green', 
        linestyle='--', 
        alpha=0.3, 
        label=f'criterion ({criterion:.0%})'
    )

    plt.legend(fontsize=12)

    plt.grid(alpha=0.3)

    plt.show()

def calculate_response_type(
    animal_id,
    from_session,
    to_session,
    stim,
    exp,
    manual_exclusion_sessions,
    difficulties,
):
    difficulties = _get_difficulties({'difficulties': difficulties})
    
    if difficulties is None:
        return

    difficulty_filter = [{'difficulty': d} for d in difficulties]
    difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')
        
    restr = exp.Session() & {'animal_id': animal_id}
    valid_sessions = (restr - exp.Session.Excluded).fetch('session')

    rows = []

    for session in range(from_session, to_session + 1):
        if session not in valid_sessions:
            continue
        
        if session in manual_exclusion_sessions:
            continue
    
        key = {'animal_id': animal_id, "session":session}

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
            rows.append(
                {
                    'session': session,
                    'state': state,
                    'n_trials': (session_trials['state'] == state).sum()
                }
            )

    response_counts = pd.DataFrame(rows)

    if response_counts.empty:
        print("🚫 No response data available for plotting.")
        return response_counts

    sessions = sorted(response_counts['session'].unique())
    session_map = {session: idx for idx, session in enumerate(sessions)}
    response_counts['session_idx'] = response_counts['session'].map(session_map)


    counts_wide = response_counts.pivot(
    index='session_idx',
    columns='state',
    values='n_trials'
    ).fillna(0)
    

    plt.figure(figsize=(max(8, len(sessions) * 1.2), 5))

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

    plt.bar(
        x - 0.18,
        counts_wide['Reward'],
        color = "#36BF00",
        width=0.3,
        label='Reward',
        zorder=2
        )
    
    plt.bar(
        x - 0.18,
        counts_wide['Punish'],
        bottom=counts_wide['Reward'],
        color = "#FF0000",
        width=0.3,
        label='Punish',
        zorder=2
        )
    
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

    plt.xlabel(
        'Session idx', 
        fontsize=18
        )

    plt.ylabel(
        'Number of trials',
        fontsize=18
    )

    plt.title(
        f'Response counts across all trial modalities (Animal: {animal_id}, Sessions: {from_session}-{to_session})',
        fontsize=18
    )

    plt.tick_params(
        axis='both',
        labelsize=12
    )

    plt.legend(
        title='Response',
        fontsize=12,
        title_fontsize=12
    )

    plt.grid(
        axis='y',
        alpha=0.3
    )

    plt.tight_layout()
    plt.show()

    return 


class obj215_trials:
    @staticmethod
    def get_multimodal_trials_summary(
        animal_id,
        from_session,
        to_session,
        manual_exclusion_sessions,
        difficulties
    ):
            
        difficulties = _get_difficulties({'difficulties': difficulties})
        
        if difficulties is None:
            return

        difficulty_filter = [{'difficulty': d} for d in difficulties]
        difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')
            
        restr = exp.Session() & {'animal_id': animal_id}
        valid_sessions = (restr - exp.Session.Excluded).fetch('session')

        rows = []

        for session in range(from_session, to_session + 1):
            if session not in valid_sessions:
                continue
            
            if session in manual_exclusion_sessions:
                continue
        
            key = {'animal_id': animal_id, "session": session}

            session_date = (exp.Session() & key).fetch1('session_tmst').strftime('%Y-%m-%d')

            licks = (
                beh.Activity.Lick()
                & key
            ).fetch(format='frame').reset_index()

            if licks.empty:
                continue

            licks['port'] = pd.to_numeric(licks['port'], errors='coerce')

            first_licks = (
                licks
                .sort_values(['trial_idx', 'time'])
                .drop_duplicates('trial_idx', keep='first')
                [['animal_id', 'session', 'trial_idx', 'port']]
                .rename(columns={'port': 'lick_port'})
            )

            lick_counts = (
                licks[licks['port'].isin([1, 2])]
                .groupby(['animal_id', 'session', 'trial_idx', 'port'])
                .size()
                .unstack(fill_value=0)
                .rename(columns={
                    1: 'lick_port1_count',
                    2: 'lick_port2_count'
                })
                .reset_index()
            )

            for column in ['lick_port1_count', 'lick_port2_count']:
                if column not in lick_counts:
                    lick_counts[column] = 0

            trial_licks = first_licks.merge(
                lick_counts[
                    [
                        'animal_id',
                        'session',
                        'trial_idx',
                        'lick_port1_count',
                        'lick_port2_count'
                    ]
                ],
                on=['animal_id', 'session', 'trial_idx'],
                how='left'
            )

            trial_licks[['lick_port1_count', 'lick_port2_count']] = (
                trial_licks[['lick_port1_count', 'lick_port2_count']]
                .fillna(0)
                .astype(int)
            )

            multi215_trials = (
                stim.StimCondition.Trial 
                * (stim.Panda.Object).proj('obj_mag')  
                * exp.Trial.StateOnset 
                * difficulty
                * (stim.Tones).proj('tone_volume', 'tone_pulse_freq') 
                & 'tone_volume > 0'
                & difficulty_filter
                & key
                & 'obj_id=215'
                & 'state in ("Reward", "Punish")'
            ).fetch(format='frame').reset_index()
        
            multi215_trials['obj_mag'] = pd.to_numeric(multi215_trials['obj_mag'], errors='coerce')    
            multi215_trials = multi215_trials[multi215_trials['obj_mag'] > 0]

            multi215_trials = multi215_trials.merge(
                trial_licks,
                on=['animal_id', 'session', 'trial_idx'],
                how='inner'
            )
            multi215_trials['lick_port'] = pd.to_numeric(multi215_trials['lick_port'], errors='coerce')

            if multi215_trials.empty:
                continue

            multi_correct = (
                (multi215_trials['tone_pulse_freq'] == 100)
                & (multi215_trials['lick_port'] == 2)
            )

            rows.append({
                'animal_id': animal_id,
                'session': session,
                'date': session_date,
                'multi_obj215_trials': len(multi215_trials),
                'multi_perf': round(multi_correct.mean(), 2),
                'rewards': (multi215_trials['state'] == 'Reward').sum(),
                'punishments': (multi215_trials['state'] == 'Punish').sum(),
                'abortions': (multi215_trials['state'] == 'Abort').sum(),
                'correct_licks': multi_correct.sum(),
                'incorrect_licks': len(multi215_trials) - multi_correct.sum(),
                'port1_licks': multi215_trials['lick_port1_count'].sum(),
                'port2_licks': multi215_trials['lick_port2_count'].sum()
                }
                )

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(rows)
    
    @staticmethod
    def get_visual_trials_summary(
        animal_id,
        from_session,
        to_session,
        manual_exclusion_sessions,
        difficulties,
    ):
            
        difficulties = _get_difficulties({'difficulties': difficulties})
        
        if difficulties is None:
            return

        difficulty_filter = [{'difficulty': d} for d in difficulties]
        difficulty = (exp.Condition.MatchPort() * exp.Trial()).proj('difficulty')
            
        restr = exp.Session() & {'animal_id': animal_id}
        valid_sessions = (restr - exp.Session.Excluded).fetch('session')

        rows = []

        for session in range(from_session, to_session + 1):
            if session not in valid_sessions:
                continue
            
            if session in manual_exclusion_sessions:
                continue
        
            key = {'animal_id': animal_id, "session": session}

            session_date = (exp.Session() & key).fetch1('session_tmst').strftime('%Y-%m-%d')

            licks = (
                beh.Activity.Lick()
                & key
            ).fetch(format='frame').reset_index()

            if licks.empty:
                continue

            licks['port'] = pd.to_numeric(licks['port'], errors='coerce')

            first_licks = (
                licks
                .sort_values(['trial_idx', 'time'])
                .drop_duplicates('trial_idx', keep='first')
                [['animal_id', 'session', 'trial_idx', 'port']]
                .rename(columns={'port': 'lick_port'})
            )

            lick_counts = (
                licks[licks['port'].isin([1, 2])]
                .groupby(['animal_id', 'session', 'trial_idx', 'port'])
                .size()
                .unstack(fill_value=0)
                .rename(columns={
                    1: 'lick_port1_count',
                    2: 'lick_port2_count'
                })
                .reset_index()
            )

            for column in ['lick_port1_count', 'lick_port2_count']:
                if column not in lick_counts:
                    lick_counts[column] = 0

            trial_licks = first_licks.merge(
                lick_counts[
                    [
                        'animal_id',
                        'session',
                        'trial_idx',
                        'lick_port1_count',
                        'lick_port2_count'
                    ]
                ],
                on=['animal_id', 'session', 'trial_idx'],
                how='left'
            )

            trial_licks[['lick_port1_count', 'lick_port2_count']] = (
                trial_licks[['lick_port1_count', 'lick_port2_count']]
                .fillna(0)
                .astype(int)
            )

            visual215_trials = (
                stim.StimCondition.Trial 
                * (stim.Panda.Object).proj('obj_mag')  
                * exp.Trial.StateOnset 
                * difficulty
                * (stim.Tones).proj('tone_volume', 'tone_pulse_freq') 
                & 'tone_volume > 0'
                & difficulty_filter
                & key
                & 'obj_id=215'
                & 'state in ("Reward", "Punish")'
            ).fetch(format='frame').reset_index()
        
            visual215_trials['obj_mag'] = pd.to_numeric(visual215_trials['obj_mag'], errors='coerce')    
            visual215_trials = visual215_trials[visual215_trials['obj_mag'] > 0]

            visual215_trials = visual215_trials.merge(
                trial_licks,
                on=['animal_id', 'session', 'trial_idx'],
                how='inner'
            )
            visual215_trials['lick_port'] = pd.to_numeric(visual215_trials['lick_port'], errors='coerce')

            if visual215_trials.empty:
                continue

            port1_first_lick = (visual215_trials['lick_port'] == 1).sum()
            port2_first_lick = (visual215_trials['lick_port'] == 2).sum()


            rows.append({
                'animal_id': animal_id,
                'session': session,
                'date': session_date,
                'visual_obj215_trials': len(visual215_trials),
                'rewards': (visual215_trials['state'] == 'Reward').sum(),
                'punishments': (visual215_trials['state'] == 'Punish').sum(),
                'abortions': (visual215_trials['state'] == 'Abort').sum(),
                'port1_first_lick': port1_first_lick,
                'port2_first_lick': port2_first_lick,
                'port1_licks': visual215_trials['lick_port1_count'].sum(),
                'port2_licks': visual215_trials['lick_port2_count'].sum()
                }
                )

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(rows)


    
























