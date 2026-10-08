"""Stimulus module for stimulus-related configurations.

Contains all visual and auditory stimulus definitions, object configurations,
and their aliases.
"""

from .objects import default_object_ids, object_aliases
from .tones import (
    tone_pulse_frequencies, 
    tone_pulse_freq_names,
    auditory_trial_criteria,
    multimodal_auditory_criteria
)

__all__ = [
    'default_object_ids',
    'object_aliases',
    'tone_pulse_frequencies',
    'tone_pulse_freq_names',
    'auditory_trial_criteria',
    'multimodal_auditory_criteria',
]