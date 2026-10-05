"""Plotting module for visualization functions.

Contains all plotting functions organized by stimulus trial type and analysis.
"""

from .visual_trials import (
    get_visual_performance_summary,
    plot_visual_performance_per_object
)
from .auditory_trials import (
    get_auditory_performance_summary,
    plot_auditory_performance_per_frequency
)
from .multimodal_trials import (
    get_multimodal_performance_summary,
    plot_multimodal_performance_per_object
)
from .distribution import (
    get_condition_distribution_data,
    plot_condition_trial_distribution,
    plot_condition_distribution_percentage
)
from .modality import (
    get_linePlot_per_modality_across_sessions,
    get_scatter_plot_modalities
)
from .responses import (
    calculate_response_type,
    plot_response_counts
)

__all__ = [
    'get_visual_performance_summary',
    'plot_visual_performance_per_object',
    'get_auditory_performance_summary',
    'plot_auditory_performance_per_frequency',
    'get_multimodal_performance_summary',
    'plot_multimodal_performance_per_object',
    'get_condition_distribution_data',
    'plot_condition_trial_distribution',
    'plot_condition_distribution_percentage',
    'get_linePlot_per_modality_across_sessions',
    'get_scatter_plot_modalities',
    'calculate_response_type',
    'plot_response_counts',
]