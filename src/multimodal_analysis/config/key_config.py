def create_analysis_key(
    animal_id,
    from_session,
    to_session,
    difficulties,
    excluded_sessions,
):
    """Create a configuration dictionary for an analysis."""
    return {
        "animal_id": animal_id,
        "sessions": (from_session, to_session),
        "difficulties": difficulties,
        "excluded_sessions": excluded_sessions,
    }