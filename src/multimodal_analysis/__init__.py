"""
Behavioral experiment analysis toolkit.

A comprehensive package for analyzing behavioral data from animal experiments,
including support for visual, auditory, and multimodal stimulus conditions.

Modules:
    db: Database configuration and schema management.
    stimuli: Stimulus definitions (objects and tones).
    utils: Validation and query helper functions.
    data: Data processing, fetching, and computation functions.
    plots: Visualization and plotting functions.

Quick Start:
    >>> from repository_name import get_schemas
    >>> from repository_name.plots import plot_visual_performance_per_object
    >>> 
    >>> schemas = get_schemas()
    >>> exp = schemas['exp']
    >>> stim = schemas['stim']
    >>> 
    >>> key = {
    ...     'animal_id': 'mouse_1',
    ...     'sessions': (1, 20),
    ...     'difficulties': [1, 2, 3],
    ...     'excluded_sessions': set()
    ... }
    >>> 
    >>> plot_visual_performance_per_object(key, stim, exp)
"""

__version__ = "0.1.0"
__author__ = "Anastasios Gratsakis"
__email__ = "gratsakisanastasios@gmail.com"
__license__ = "MIT"


# Database imports
from .db.config import get_schemas, SCHEMATA

# Stimulus configuration imports
from .stimuli.objects import default_object_ids, object_aliases
from .stimuli.tones import (
    tone_pulse_frequencies,
    tone_pulse_freq_names,
    auditory_trial_criteria,
    multimodal_auditory_criteria
)

# Utility imports
from .utils.validators import validate_key, get_difficulties
from .utils.queries import fetch_sessions

# Data Processing Imports
from .data.processors import process_visual_object, process_multimodal_object
from .data.fetchers import fetch_visual_data, fetch_multimodal_data
from .data.computers import (
    compute_auditory_performance_summary,
    compute_modality_performance
)

# Plotting imports
from .plots.visual_trials import (
    get_visual_performance_summary,
    plot_visual_performance_per_object
)
from .plots.auditory_trials import (
    get_auditory_performance_summary,
    plot_auditory_performance_per_frequency
)
from .plots.multimodal_trials import (
    get_multimodal_performance_summary,
    plot_multimodal_performance_per_object
)
from .plots.distribution import (
    get_condition_distribution_data,
    plot_condition_trial_distribution,
    plot_condition_distribution_percentage
)
from .plots.modality import (
    get_linePlot_per_modality_across_sessions,
    get_scatter_plot_modalities
)
from .plots.responses import (
    calculate_response_type,
    plot_response_counts
)

# Public API
__all__ = [
    # Version and metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    
    # Database
    'get_schemas',
    'SCHEMATA',
    
    # Stimuli
    'default_object_ids',
    'object_aliases',
    'tone_pulse_frequencies',
    'tone_pulse_freq_names',
    'auditory_trial_criteria',
    'multimodal_auditory_criteria',
    
    # Utils
    'validate_key',
    'get_difficulties',
    'fetch_sessions',
    
    # Data - Processors
    'process_visual_object',
    'process_multimodal_object',
    
    # Data - Fetchers
    'fetch_visual_data',
    'fetch_multimodal_data',
    
    # Data - Computers
    'compute_auditory_performance_summary',
    'compute_modality_performance',
    
    # Plots - Visual trials
    'get_visual_performance_summary',
    'plot_visual_performance_per_object',
    
    # Plots - Auditory trials
    'get_auditory_performance_summary',
    'plot_auditory_performance_per_frequency',
    
    # Plots - Multimodal trials
    'get_multimodal_performance_summary',
    'plot_multimodal_performance_per_object',
    
    # Plots - Distribution
    'get_condition_distribution_data',
    'plot_condition_trial_distribution',
    'plot_condition_distribution_percentage',
    
    # Plots - Modality
    'get_linePlot_per_modality_across_sessions',
    'get_scatter_plot_modalities',
    
    # Plots - Responses
    'calculate_response_type',
    'plot_response_counts',
]