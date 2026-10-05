"""Data module for fetching and computing analysis data.

Contains functions for processing trial data, fetching performance metrics,
and computing statistics across different stimulus modalities.
"""

from .processors import process_visual_object, process_multimodal_object
from .fetchers import fetch_visual_data, fetch_multimodal_data
from .computers import (
    compute_auditory_performance_summary, 
    compute_modality_performance
)

__all__ = [
    'process_visual_object',
    'process_multimodal_object',
    'fetch_visual_data',
    'fetch_multimodal_data',
    'compute_auditory_performance_summary',
    'compute_modality_performance',
]