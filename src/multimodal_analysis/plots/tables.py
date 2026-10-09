"""Styling utilities for behavioral data tables.

This module provides helper functions for formatting and highlighting
pandas DataFrames, including visual and audiovisual trial distributions.
"""

def highlight_object_trials_distribution_table(value):
    """Highlight cells according to modality-specific trial availability.

    Args:
        value (str): Cell value formatted as 'visual / audiovisual'.

    Returns:
        str: CSS background-color styling, or an empty string when
        highlighting is not required or the value is invalid.
    """
    if not isinstance(value, str):
        return ""

    try:
        visual, audiovisual = map(
            int,
            value.split(" / "),
        )
    except ValueError:
        return ""

    if visual < 0 or audiovisual < 0:
        return ""

    if visual == 0 and audiovisual == 0:
        return ""

    if visual == 0 or audiovisual == 0:
        return "background-color: orange"

    return "background-color: lightgreen"