"""Styling utilities for behavioral data tables.

This module provides helper functions for formatting and highlighting
pandas DataFrames, including visual and audiovisual trial distributions.
"""

def highlight_object_trials_distribution_table(value):
    """Highlight object trial counts according to modality availability.

    Args:
        value: Cell value formatted as 'visual / audiovisual'.

    Returns:
        str: CSS styling for the table cell, or an empty string if no
            highlighting is required.
    """
    if not isinstance(value, str):
        return ""

    visual, audiovisual = map(int, value.split(" / "))

    # Neither modality was presented: no highlighting.
    if visual == 0 and audiovisual == 0:
        return ""

    # The object was presented in only one modality.
    if visual == 0 or audiovisual == 0:
        return "background-color: orange"

    # The object was presented in both modalities.
    return "background-color: lightgreen"