"""
Tone definitions and configurations for auditory stimuli.

This module contains all tone-related constants and configurations
used in auditory and multimodal trials.
"""

# Tone pulse frequency configuration

TONE_FREQUENCIES = [0, 100]
"""List of tone pulse frequencies used in experiments.

- 0 Hz: Continuous tone
- 100 Hz: Pulsed tone
"""

TONE_FREQUENCY_NAMES = {
    0: 'Continuous tone',
    100: 'Pulsed tone'
}
"""Mapping of tone pulse frequencies to descriptive names."""


# Tone volume configuration 

MIN_AUDIBLE_VOLUME = 0
"""Minimum volume threshold that constitutes auditory stimulation."""

# Auditory trials definitions

AUDITORY_TRIAL_CRITERIA = {
    'tone_volume': '> 0',
    'obj_mag': '== 0'
}
"""Criteria defining auditory trials in the database.

Auditory trials have:
- tone_volume > 0 (auditory stimulus present)
- obj_mag == 0 (no visual stimulus)
"""

MULTIMODAL_AUDITORY_CRITERIA = {
    'tone_volume': '> 0',
    'obj_mag': '> 0'
}
"""Criteria defining multimodal trials with auditory component.

Multimodal trials have:
- tone_volume > 0 (auditory stimulus present)
- obj_mag > 0 (visual stimulus present)
"""