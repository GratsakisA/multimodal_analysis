"""Stimulus module for stimulus-related configurations.

Contains all visual and auditory stimulus definitions, object configurations,
and their aliases.
"""

from .objects import DEFAULT_OBJECT_IDS, OBJECT_ALIASES
from .tones import (
    TONE_FREQUENCIES, 
    TONE_FREQUENCY_NAMES,
    AUDITORY_TRIAL_CRITERIA,
    MULTIMODAL_AUDITORY_CRITERIA
)

__all__ = [
    'DEFAULT_OBJECT_IDS',
    'OBJECT_ALIASES',
    'TONE_FREQUENCIES',
    'TONE_FREQUENCY_NAMES',
    'AUDITORY_TRIAL_CRITERIA',
    'MULTIMODAL_AUDITORY_CRITERIA',
]