"""
Cross-modality comparison plotting functions.

This module contains functions for comparing performance across different
stimulus modalities (auditory, visual, multimodal).
"""

import matplotlib.pyplot as plt
import seaborn as sns

from multimodal_analysis.data.computers import compute_modality_performance


def get_linePlot_per_modality_across_sessions(
    key, stim, exp, criterion=0.65
):
    """Plot performance across sessions for each modality.

    Args:
        key (dict): Analysis configuration containing:
            - animal_id (int): Animal identifier.
            - sessions (tuple): Start and end session numbers.
            - difficulties (list): Difficulty levels to include.
            - excluded_sessions (list or set): Sessions to exclude.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.
        criterion (float, optional): Performance criterion.
            Defaults to 0.65 (65%).

    Returns:
        None: Displays the plot.
    """
    animal_id = key["animal_id"]
    from_session, to_session = key["sessions"]

    perf_per_modality = compute_modality_performance(
        key, stim, exp
    )

    if perf_per_modality is None:
        return

    if perf_per_modality.empty:
        print("No data available for plotting.")
        return

    perf_per_modality = perf_per_modality.sort_values(
        "session"
    ).copy()

    sessions = perf_per_modality["session"].tolist()
    perf_per_modality["session_idx"] = range(
        len(perf_per_modality)
    )

    perf_long = perf_per_modality.melt(
        id_vars=["session", "session_idx"],
        value_vars=[
            "auditory_perf",
            "visual_perf",
            "multi_perf",
            "multi_difficult_perf",
            "visual_difficult_perf",
        ],
        var_name="modality",
        value_name="performance",
    ).dropna(subset=["performance"])

    perf_long["modality"] = perf_long["modality"].map({
        "auditory_perf": "Auditory",
        "visual_perf": "Visual",
        "multi_perf": "Multimodal",
        "multi_difficult_perf": "Multimodal Difficult",
        "visual_difficult_perf": "Visual Difficult",
    })

    if perf_long.empty:
        print("No modality performance data available for plotting.")
        return

    plt.figure(figsize=(max(8, len(sessions) * 1.2), 5))

    sns.lineplot(
        data=perf_long,
        x="session_idx",
        y="performance",
        hue="modality",
        marker="o",
    )

    plt.title(
        f"Performance across sessions in each modality\n"
        f"(Animal: {animal_id}, "
        f"Sessions: {from_session}-{to_session})",
        fontsize=18,
    )

    plt.xlabel("Session index", fontsize=18)
    plt.ylabel("Performance", fontsize=18)

    plt.xticks(
        ticks=range(len(sessions)),
        labels=sessions,
        rotation=80,
    )

    plt.ylim(0, 1.1)
    plt.tick_params(axis="both", labelsize=16)

    plt.axhline(
        0.5,
        color="grey",
        linestyle="--",
        alpha=0.3,
        label="Chance",
    )

    plt.axhline(
        criterion,
        color="green",
        linestyle="--",
        alpha=0.3,
        label=f"Criterion ({criterion:.0%})",
    )

    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

def get_scatter_plot_modalities(key, stim, exp):
    """Plot performance comparisons across sensory modalities.

    Creates four scatter plots comparing auditory, visual, and
    multimodal performance across sessions.

    Args:
        key (dict): Analysis configuration containing:
            - animal_id: Animal identifier.
            - sessions: (start_session, end_session).
            - difficulties: Difficulty levels to include.
            - excluded_sessions: Sessions to exclude.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.

    Returns:
        None: Displays the scatter plots.
    """
    animal_id = key["animal_id"]

    perf_per_condition = compute_modality_performance(
        key=key,
        stim=stim,
        exp=exp
    )

    if perf_per_condition.empty:
        print("🚫 No valid data for plotting")
        return

    perf_per_condition["session"] = (
        perf_per_condition["session"].astype(str)
    )

    # Create 4-subplot figure
    fig, axes = plt.subplots(1, 4, figsize=(15, 5), sharex=True, sharey=False)
    
    # PLOT 1: Auditory vs Visual
    sns.scatterplot(
        data=perf_per_condition,
        x='auditory_perf',
        y='visual_perf',
        ax=axes[0],
        hue='session',
        s=40,
        legend=False
    )
    axes[0].set_title('Auditory vs Visual', fontsize=12)
    axes[0].set_ylabel('visual_perf', fontsize=12)
    axes[0].set_xlabel('auditory_perf', fontsize=12)
    axes[0].tick_params(axis='both', labelsize=12)
    axes[0].set_xlim(0, 1.1)
    axes[0].set_ylim(0, 1.1)
    axes[0].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    # PLOT 2: Visual vs Multimodal
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
    axes[1].set_ylabel('multimodal_perf', fontsize=12)
    axes[1].set_xlabel('visual_perf', fontsize=12)
    axes[1].tick_params(axis='both', labelsize=12)
    axes[1].set_xlim(0, 1.1)
    axes[1].set_ylim(0, 1.1)
    axes[1].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    # PLOT 3: Auditory vs Multimodal
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
    axes[2].set_ylabel('multimodal_perf', fontsize=12)
    axes[2].set_xlabel('auditory_perf', fontsize=12)
    axes[2].tick_params(axis='both', labelsize=12)
    axes[2].set_xlim(0, 1.1)
    axes[2].set_ylim(0, 1.1)
    axes[2].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    # PLOT 4: Unimodals vs Multimodal
    # Compute unimodal average
    perf_per_condition['uni_perf'] = perf_per_condition[
        ['auditory_perf', 'visual_perf']
    ].mean(axis=1, skipna=True)
    
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
    axes[3].set_ylabel('multimodal_perf', fontsize=12)
    axes[3].set_xlabel('unimodal_perf', fontsize=12)
    axes[3].tick_params(axis='both', labelsize=12)
    axes[3].set_xlim(0, 1.1)
    axes[3].set_ylim(0, 1.1)
    axes[3].axline((0, 0), slope=1, linestyle='--', color='gray')
    
    plt.suptitle(
        f'Performance Across Auditory, Visual, and Multimodal Conditions '
        f'(Animal {animal_id})',
        fontsize=14
    )
    
    plt.tight_layout()
    plt.show()
