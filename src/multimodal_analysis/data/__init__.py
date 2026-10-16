"""Data module for fetching and computing analysis data.

Contains functions for processing trial data, fetching performance metrics,
and computing statistics across different stimulus modalities.
"""

from .computers import (
    compute_auditory_performance_summary,
    compute_modality_performance,
)
from .fetchers import fetch_multimodal_data, fetch_visual_data
from .processors import (
    process_multimodal_object,
    process_visual_object,
)

__all__ = [
    "compute_auditory_performance_summary",
    "compute_modality_performance",
    "fetch_multimodal_data",
    "fetch_visual_data",
    "process_multimodal_object",
    "process_visual_object",
]