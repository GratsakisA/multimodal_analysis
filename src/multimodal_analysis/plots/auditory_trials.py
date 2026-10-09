"""
Auditory performance plotting functions.

This module contains functions for visualizing performance in auditory trials,
separated by tone frequency (continuous vs pulsed).
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from IPython.display import display, HTML
from ..data.computers import compute_auditory_performance_summary
from ..stimuli.tones import tone_pulse_freq_names, tone_pulse_frequencies
from ..utils.validators import validate_key


def get_auditory_performance_summary(key, stim, exp, pulse_freq='all'):
    """Fetch and display auditory performance data in Jupyter.
    
    Retrieves auditory performance for continuous and/or pulsed tones
    and displays them as formatted tables in the notebook.
    
    Args:
        key (dict): Analysis key dictionary with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session) range
            - difficulties (int or list): Difficulty level(s)
            - excluded_sessions (set, optional): Sessions to exclude
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        pulse_freq (str or int, optional): Which tone types to display.
            - 'all': Display both continuous and pulsed (default)
            - 0: Display only continuous tone (0 Hz)
            - 100: Display only pulsed tone (100 Hz)
        
    Returns:
        tuple: (pulse0_df, pulse100_df) DataFrames.
        
    Raises:
        ValueError: If pulse_freq is not 'all', 0, or 100.
        
    Example:
        >>> key = {'animal_id': 'mouse_1', 'sessions': (1, 20), 'difficulties': [1, 2]}
        >>> p0, p100 = get_auditory_performance_summary(key, stim, exp, pulse_freq='all')
    """
    pulse0_df, pulse100_df = compute_auditory_performance_summary(key, stim, exp)

    if pulse0_df.empty and pulse100_df.empty:
        print("🚫 No valid auditory data for analysis")
        return pulse0_df, pulse100_df

    display(HTML("<h2><b>Unimodal auditory trials</b></h2>"))
    
    if pulse_freq == 'all':
        display(HTML(
            f'<b><h4>{tone_pulse_freq_names[100]}</b> '
            f'(<i>tone_pulse_freq = 100 Hz</i>)</h4>'
        ))
        display(pulse100_df)
    
        display(HTML(
            f'<b><h4>{tone_pulse_freq_names[0]}</b> '
            f'(<i>tone_pulse_freq = 0 Hz</i>)</h4>'
        ))
        display(pulse0_df)

    elif pulse_freq == 0:
        display(HTML(
            f'<b><h4>{tone_pulse_freq_names[0]}</b> '
            f'(<i>tone_pulse_freq = 0 Hz</i>)</h4>'
        ))
        display(pulse0_df)
    
    elif pulse_freq == 100:
        display(HTML(
            f'<b><h4>{tone_pulse_freq_names[100]}</b> '
            f'(<i>tone_pulse_freq = 100 Hz</i>)</h4>'
        ))
        display(pulse100_df)
        
    else:
        raise ValueError("pulse_freq must be 'all', 0, or 100")

    return pulse0_df, pulse100_df


def plot_auditory_performance_per_frequency(key, stim, exp, criterion=0.65):
    """Plot auditory performance by tone frequency.
    
    Creates two subplots: a line plot showing performance trajectory for each
    tone type across sessions, and a bar plot with 95% confidence intervals
    for mean performance by tone frequency.
    
    Args:
        key (dict): Analysis key dictionary with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session) range
            - difficulties (int or list): Difficulty level(s)
            - excluded_sessions (set, optional): Sessions to exclude
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        criterion (float, optional): Performance criterion line.
            Defaults to 0.65 (65%).
        
    Returns:
        None: Displays plot using plt.show().
        
    Example:
        >>> plot_auditory_performance_per_frequency(key, stim, exp, criterion=0.65)
    """
    validate_key(key)
    
    animal_id = key['animal_id']
    from_s, to_s = key['sessions']
    
    pulse0_df, pulse100_df = compute_auditory_performance_summary(key, stim, exp)

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

    fig, axes = plt.subplots(
        1, 2, 
        figsize=(18, 5),
        constrained_layout=True
    )
    
    # LINE PLOT - Performance across sessions by tone type
    for freq in tone_pulse_frequencies:
        df_sub = df_all[df_all['tone_pulse_freq'] == freq]
        axes[0].plot(
            df_sub['session_idx'],
            df_sub['performance'],
            marker='o',
            label=tone_pulse_freq_names[freq]
        )

    axes[0].set_title(
        'Auditory performance across sessions', 
        fontsize=18
    )
    axes[0].set_xticks(range(len(sessions_all)))
    axes[0].set_xticklabels(sessions_all, rotation=80)
    axes[0].tick_params(axis='both', labelsize=16)
    axes[0].set_xlabel('Session idx', fontsize=18)
    axes[0].set_ylabel('Performance', fontsize=18)
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

    # BAR PLOT - Mean performance by tone frequency
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
    axes[1].tick_params(axis='both', labelsize=16)
    axes[1].set_xticklabels(
        [tone_pulse_freq_names[0], tone_pulse_freq_names[100]], 
        fontsize=16
    )
    axes[1].set_title('Mean auditory performance (±95% CI)', fontsize=18)
    axes[1].set_xlabel('Tone type', fontsize=18)
    axes[1].set_ylabel('Mean performance', fontsize=18)
    axes[1].set_ylim(0, 1.1)
    axes[1].axhline(0.5, color='grey', linestyle='--', alpha=0.3)
    axes[1].axhline(criterion, color='green', linestyle='--', alpha=0.3)

    if axes[1].get_legend():
        axes[1].get_legend().remove()

    plt.suptitle(
        f"Performance in unimodal $\\mathbf{{auditory}}$ trials by tone type "
        f"(Animal {animal_id}, sessions: {from_s}-{to_s})",
        fontsize=14
    )
    
    plt.show()