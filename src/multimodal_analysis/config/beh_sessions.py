import json
from pathlib import Path


SESSIONS_PATH = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "beh_sessions.json"
)


def _load_sessions():
    with SESSIONS_PATH.open("r") as f:
        return json.load(f)


def _save_sessions(sessions):
    with SESSIONS_PATH.open("w") as f:
        json.dump(sessions, f, indent=4)


def add_behavior_sessions(animal_id, task_type, sessions):
    """Add behavioral sessions for an animal and task type."""
    data = _load_sessions()

    animal_id = str(animal_id)

    data.setdefault(animal_id, {})
    data[animal_id].setdefault(task_type, [])

    # Check all sessions for this animal before modifying the data.
    for session in sessions:
        for group, group_sessions in data[animal_id].items():
            if session in group_sessions:
                raise ValueError(
                    f"Session {session} for animal {animal_id} "
                    f"already exists in task type '{group}'."
                )

    # No conflicts found → add the sessions.
    data[animal_id][task_type].extend(sessions)
    data[animal_id][task_type].sort()

    _save_sessions(data)

def get_behavior_sessions(animal_id, task_type=None):
    """Get behavioral sessions for an animal and task type."""
    data = _load_sessions()

    animal_id = str(animal_id)
    animal_data = data.get(animal_id, {})

    if task_type is not None:
        return animal_data.get(task_type, [])

    return animal_data

def remove_behavior_sessions(animal_id, task_type, sessions):
    """Remove behavioral sessions for an animal and task type."""

    data = _load_sessions()

    animal_id = str(animal_id)

    if animal_id not in data:
        raise ValueError(f"Animal {animal_id} not found.")

    if task_type not in data[animal_id]:
        raise ValueError(
            f"Task type '{task_type}' not found for animal {animal_id}."
        )

    existing_sessions = data[animal_id][task_type]

    # Check all sessions before modifying the data.
    for session in sessions:
        if session not in existing_sessions:
            raise ValueError(
                f"Session {session} not found for animal {animal_id} "
                f"and task type '{task_type}'."
            )

    for session in sessions:
        existing_sessions.remove(session)

    _save_sessions(data)