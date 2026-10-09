"""Plotting module for visualization functions.

Contains all plotting functions organized by stimulus trial type and analysis.
"""

from .visual_trials import (
    get_visual_performance_summary,
    plot_visual_performance_per_object,
)
from .auditory_trials import (
    get_auditory_performance_summary,
    plot_auditory_performance_per_frequency,
)
from .multimodal_trials import (
    get_multimodal_performance_summary,
    plot_multimodal_performance_per_object,
)
from .distribution import (
    get_condition_distribution_data,
    plot_condition_trial_distribution,
    plot_condition_distribution_percentage,
    get_object_distribution_trials,
    # get_object_distribution_data,
    # plot_object_distribution_object_trials,
)

from .tables import highlight_object_trials_distribution_table

from .modality import (
    get_linePlot_per_modality_across_sessions,
    get_scatter_plot_modalities,
)
from .responses import (
    calculate_response_type,
    plot_response_counts,
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
    'get_object_distribution_trials',
    'highlight_object_trials_distribution_table',
    # 'plot_object_distribution_object_trials',
    # 'get_object_distribution_data',
    
]