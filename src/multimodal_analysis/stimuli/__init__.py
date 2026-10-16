"""Stimulus module for stimulus-related configurations.

Contains all visual and auditory stimulus definitions, object configurations,
and their aliases.
"""

from .objects import default_object_ids, object_aliases
from .tones import (
    auditory_trial_criteria,
    multimodal_auditory_criteria,
    tone_pulse_freq_names,
    tone_pulse_frequencies,
)

__all__ = [
    'auditory_trial_criteria',
    'default_object_ids',
    'multimodal_auditory_criteria',
    'object_aliases',
    'tone_pulse_freq_names',
    'tone_pulse_frequencies',
]