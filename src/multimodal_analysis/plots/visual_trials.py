"""
Visual performance plotting functions.

This module contains functions for visualizing performance in visual trials,
including line plots across sessions and bar plots with confidence intervals.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from IPython.display import display, HTML
from ..data.fetchers import fetch_visual_data
from ..utils.validators import validate_key


def get_visual_performance_summary(key, stim, exp):
    """Fetch and display visual performance data in Jupyter.
    
    Retrieves visual performance DataFrames for each object and displays
    them as formatted tables in the notebook.
    
    Args:
        key (dict): Analysis key dictionary with keys:
            - animal_id (str): Animal identifier
            - sessions (tuple): (from_session, to_session) range
            - difficulties (int or list): Difficulty level(s)
            - excluded_sessions (set, optional): Sessions to exclude
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        
    Returns:
        dict: Dictionary mapping object_id to pd.DataFrame, or empty dict
              if no data found.
              
    Example:
        >>> key = {
        ...     'animal_id': 'mouse_1',
        ...     'sessions': (1, 20),
        ...     'difficulties': [1, 2, 3]
        ... }
        >>> object_dfs = get_visual_performance_summary(key, stim, exp)
    """
    object_dfs = fetch_visual_data(key, stim, exp)

    if not object_dfs:
        print("🚫 No valid visual data to analyze.")
        return object_dfs
    
    display(HTML("<h2><b>Unimodal visual trials</b></h2>"))    
    
    for obj_id, df in object_dfs.items():
        print(f"Object {obj_id}:")
        display(df)
        
    return object_dfs


def plot_visual_performance_per_object(key, stim, exp, criterion=0.65):
    """Plot visual performance across objects and sessions.
    
    Creates two subplots: a line plot showing performance trajectory across
    sessions, and a bar plot with 95% confidence intervals for mean performance.
    Includes criterion line and sample size annotations.
    
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
        >>> plot_visual_performance_per_object(key, stim, exp, criterion=0.65)
    """
    validate_key(key)
    
    animal_id = key['animal_id']
    from_s, to_s = key['sessions']
    
    object_dfs = fetch_visual_data(key, stim, exp)
    
    row_data = []
    
    for obj_id, df in object_dfs.items():
        if not df.empty:
            df_copy = df.copy()
            df_copy['object'] = str(obj_id)
            row_data.append(
                df_copy[[
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
            print(f"🫠 Skipped file for object {obj_id}. Empty or malformed.")
    
    if not row_data:
        print("🚫 No valid visual data to plot.")
        return

    row_data = pd.concat(row_data, ignore_index=True)
    row_data['session'] = pd.to_numeric(row_data['session'])

    sessions = sorted(row_data["session"].unique())
    session_map = {s: i for i, s in enumerate(sessions)}
    row_data["session_idx"] = row_data["session"].map(session_map)

    # LINE PLOT - Performance across sessions
    fig, axes = plt.subplots(
        1, 2, 
        figsize=(18, 5),
        constrained_layout=True
    )
    
    sns.lineplot(
        data=row_data, 
        x='session_idx', 
        y='performance', 
        hue='object', 
        marker='o', 
        ax=axes[0]
    )
    
    axes[0].set_title(
        "Visual performance across sessions",
        fontsize=18
    )
    axes[0].set_xlabel('Session idx', fontsize=18)
    axes[0].set_ylabel('Performance', fontsize=18)
    axes[0].set_ylim(0, 1.1)
    axes[0].grid(alpha=0.2)
    axes[0].axhline(
        y=0.5, 
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
    axes[0].tick_params(axis='both', labelsize=16)
    axes[0].set_axisbelow(True)
    axes[0].legend(fontsize=8)
    axes[0].set_xticks(range(len(sessions)))
    axes[0].set_xticklabels(sessions, rotation=80)

    # BAR PLOT - Mean performance per object
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
    axes[1].set_ylabel('Mean performance', fontsize=18)
    axes[1].set_xlabel('Object ids', fontsize=18)
    axes[1].tick_params(axis='both', labelsize=16)
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
    
    # Remove legend from bar plot
    if axes[1].get_legend():
        axes[1].get_legend().remove()

    # Add annotations - sample size and trial counts
    total_trials_per_object = row_data.groupby('object')['valid_obj_trials'].sum()
    
    for i, obj in enumerate(sorted(row_data['object'].unique())):
        n_sessions = row_data[row_data['object'] == obj].shape[0]
        n_trials = int(total_trials_per_object[obj])
        
        axes[1].text(
            i, 
            0.05,
            f'sessions={n_sessions}\ntrials={n_trials}',
            ha='center',
            fontsize=10, 
            color='black', 
            bbox=dict(
                facecolor='white',
                edgecolor='none',
                alpha=0.5, 
                pad=5
            )
        )
        
    plt.suptitle(
        f"Performance in unimodal $\\mathbf{{visual}}$ trials for each object "
        f"(animal: {animal_id}, sessions: {from_s}-{to_s})",
        fontsize=14
    )
    
    plt.show()