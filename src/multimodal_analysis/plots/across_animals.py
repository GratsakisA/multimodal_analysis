"""
Plotting functions across animals

This module contains functions for comparing performance across different
stimulus modalities (auditory, visual, multimodal) across animals.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from multimodal_analysis.data.computers import compute_modality_performance


def plot_modalities_across_animals_scatter(keys, stim, exp):
    """Plot performance comparisons across sensory modalities for multiple animals.

    Creates four scatter plots comparing auditory, visual, and
    multimodal performance across animals and sessions.

    Args:
        keys (list[dict]): Analysis configurations, one per animal.
        stim: DataJoint stimuli schema.
        exp: DataJoint experiments schema.

    Returns:
        pd.DataFrame: Combined performance data across animals.
    """
    results = []

    for key in keys:
        perf_per_condition = compute_modality_performance(
            key=key,
            stim=stim,
            exp=exp,
        )

        if perf_per_condition.empty:
            print(f"No valid data for animal {key['animal_id']}")
            continue

        # Identify the animal associated with each observation.
        perf_per_condition = perf_per_condition.copy()
        perf_per_condition["animal_id"] = key["animal_id"]

        results.append(perf_per_condition)

    if not results:
        print("No valid data for plotting.")
        return pd.DataFrame()

    # Combine all animals into one DataFrame.
    perf_per_condition = pd.concat(results, ignore_index=True)

    # Compute average unimodal performance.
    perf_per_condition["uni_perf"] = perf_per_condition[
        ["auditory_perf", "visual_perf"]
    ].mean(axis=1, skipna=True)

    # Define the four modality comparisons.
    comparisons = [
        ("auditory_perf", "visual_perf", "Auditory vs Visual"),
        ("visual_perf", "multi_perf", "Visual vs Multimodal"),
        ("auditory_perf", "multi_perf", "Auditory vs Multimodal"),
        ("uni_perf", "multi_perf", "Unimodal vs Multimodal"),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(18, 5), sharex=True, sharey=True)

    for ax, (x_col, y_col, title) in zip(axes, comparisons):
        sns.scatterplot(
            data=perf_per_condition,
            x=x_col,
            y=y_col,
            hue="animal_id",
            palette="tab10",
            s=50,
            alpha=0.8,
            ax=ax,
        )

        ax.set_title(title, fontsize=12)
        ax.set_xlabel(x_col, fontsize=10)
        ax.set_ylabel(y_col, fontsize=10)
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        ax.axline((0, 0), slope=1, linestyle="--", color="gray")
        ax.tick_params(axis="both", labelsize=10)

    # Use one shared legend for all four plots.
    handles, labels = axes[0].get_legend_handles_labels()

    for ax in axes:
        if ax.legend_ is not None:
            ax.legend_.remove()

    fig.legend(
        handles,
        labels,
        title="Animal ID",
        loc="center left",
        bbox_to_anchor=(0.90, 0.5),
    )

    fig.suptitle(
        f"Performance Across Sensory Modalities and Animals (n={len(animal_configs)})",
        fontsize=14,
    )

    plt.tight_layout(rect=(0, 0, 0.90, 0.93))
    plt.show()

    return ax