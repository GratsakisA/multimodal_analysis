"""Plotting module for visualization functions.

Contains all plotting functions organized by stimulus trial type and analysis.
"""

from .auditory_trials import (
    get_auditory_performance_summary,
    plot_auditory_performance_per_frequency,
)
from .distribution import (
    get_condition_distribution_data,
    get_object_distribution_trials,
    # get_object_distribution_data,
    # plot_object_distribution_object_trials,
    plot_condition_distribution_percentage,
    plot_condition_trial_distribution,
)
from .modality import (
    plot_modalities_across_sessions_line,
    plot_modalities_across_sessions_scatter,
)
from .across_animals import (
    plot_modalities_across_animals_scatter,
    # plot_modalities_across_animals_line,
)
from .multimodal_trials import (
    get_multimodal_performance_summary,
    plot_multimodal_performance_per_object,
)
from .responses import (
    calculate_response_type,
    plot_response_counts,
)
from .tables import highlight_object_trials_distribution_table
from .visual_trials import (
    get_visual_performance_summary,
    plot_visual_performance_per_object,
)

__all__ = [
    'calculate_response_type',
    'get_auditory_performance_summary',
    'get_condition_distribution_data',
    'plot_modalities_across_sessions_line',
    'get_multimodal_performance_summary',
    'get_object_distribution_trials',
    'plot_modalities_across_sessions_scatter',
    'get_visual_performance_summary',
    'highlight_object_trials_distribution_table',
    'plot_auditory_performance_per_frequency',
    'plot_condition_distribution_percentage',
    'plot_condition_trial_distribution',
    'plot_multimodal_performance_per_object',
    'plot_response_counts',
    'plot_visual_performance_per_object',
    # 'plot_object_distribution_object_trials',
    # 'get_object_distribution_data',
    
]