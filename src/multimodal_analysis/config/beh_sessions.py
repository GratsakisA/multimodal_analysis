import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

SESSIONS_PATH = Path(__file__).resolve().parents[3] / "config" / "beh_sessions.json"


def _load_sessions():
    with SESSIONS_PATH.open("r") as f:
        return json.load(f)


def _save_sessions(sessions):
    with SESSIONS_PATH.open("w") as f:
        json.dump(sessions, f, indent=4)


def get_animal_ids():
    """Get all animal IDs defined in the behavioral session configuration.

    Returns:
        list[str]: Sorted list of animal IDs, ordered numerically.
    """

    data = _load_sessions()
    return sorted(data.keys(), key=int)


def add_behavior_sessions(animal_id, task_type, sessions):
    """Add behavioral sessions for an animal and task type.

    Adds the specified sessions to the behavioral session configuration.
    Checks for existing sessions across all task types for the animal
    before modifying the configuration.

    Args:
        animal_id (int or str): Identifier of the animal.
        task_type (str): Behavioral task type associated with the sessions.
        sessions (list[int]): Session IDs to add.

    Raises:
        ValueError: If any session already exists for the animal under
            any task type.
    """
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


def get_behavior_sessions(animal_id=None, task_type=None):
    """Get behavioral sessions filtered by animal and task type(s).

    Args:
        animal_id (int or str, optional): Animal identifier.
            If None, retrieves sessions for all animals.
        task_type (str or list[str], optional): Task type(s) to retrieve.
            If None, retrieves all task types.

    Returns:
        dict or list:
            - If animal_id is None and task_type is None, returns the
              complete session configuration.
            - If animal_id is None and task_type is specified, returns
              a dictionary mapping each animal ID to a combined,
              sorted list of sessions.
            - If animal_id is specified and task_type is None, returns
              a dictionary mapping task types to session lists.
            - If animal_id and task_type are specified, returns a
              combined, sorted list of sessions.

    Raises:
        TypeError: If task_type is neither a string, a list of strings,
            nor None.
    """
    data = _load_sessions()

    # Normalize task_type to a list.
    if isinstance(task_type, str):
        task_types = [task_type]
    else:
        task_types = task_type

    # All animals
    if animal_id is None:
        if task_types is None:
            return data

        return {
            animal: sorted(
                session for task in task_types for session in animal_data.get(task, [])
            )
            for animal, animal_data in data.items()
        }

    # Specific animal
    animal_id = str(animal_id)
    animal_data = data.get(animal_id, {})

    if task_types is None:
        return animal_data

    return sorted(
        session for task in task_types for session in animal_data.get(task, [])
    )


def remove_behavior_sessions(animal_id, task_type, sessions):
    """Remove behavioral sessions for an animal and task type.

    Removes the specified sessions from the behavioral session
    configuration. Checks that the animal, task type, and all
    specified sessions exist before modifying the configuration.

    Args:
        animal_id (int or str): Identifier of the animal.
        task_type (str): Behavioral task type associated with the sessions.
        sessions (list[int]): Session IDs to remove.

    Raises:
        ValueError: If the animal or task type is not found, or if any
            specified session does not exist for the given animal
            and task type.
    """

    data = _load_sessions()

    animal_id = str(animal_id)

    if animal_id not in data:
        raise ValueError(f"Animal {animal_id} not found.")

    if task_type not in data[animal_id]:
        raise ValueError(f"Task type '{task_type}' not found for animal {animal_id}.")

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


def get_task_types(animal_id=None):
    """Return unique task types.

    Retrieves task types names defined in the beh-session
    configuration file.

    Args:
        animal_id (int or str, optional): Animal identifier used to
            filter configurations. If ``None``, includes all animals.

    Returns:
        list[str]: Alphabetically sorted, unique task_types configurations.
            Returns an empty list if no configurations are defined.
    """
    data = _load_sessions()

    if animal_id is not None:
        animal_data = data.get(str(animal_id), {})
        task_type = animal_data.keys()
    else:
        task_type = {
            task_type for animal_data in data.values() for task_type in animal_data
        }

    return sorted(task_type)


def plot_behavior_task_types(show_counts=False):
    """Plot which behavioral task types have been run for each animal.

    Args:
        show_counts (bool, optional):
            If True, display the number of sessions per task type.
            If False, display task-type presence or absence.
            Defaults to False.

    Returns:
        tuple: Matplotlib figure and axes.
    """
    data = get_behavior_sessions()

    if not data:
        raise ValueError("No behavioral session configurations found.")

    # Define the preferred task-type order.
    task_type_order = [
        "visual",
        "audiovisual",
        "audiovisual_diff",
        "audiovisual_obj215",
        "audiovisual_conflicted",
        "audiovisual_no_stim",
    ]

    # Collect all task types across animals.
    available_task_types = {
        task_type for animal_data in data.values() for task_type in animal_data
    }

    if not available_task_types:
        raise ValueError("No task types found in the configuration.")

    # Apply the preferred order and retain any additional task types.
    task_types = [
        task_type for task_type in task_type_order if task_type in available_task_types
    ]

    task_types.extend(sorted(available_task_types - set(task_types)))

    # Sort numeric animal IDs numerically.
    animal_ids = sorted(
        data.keys(),
        key=lambda animal_id: (
            (0, int(animal_id)) if str(animal_id).isdigit() else (1, str(animal_id))
        ),
    )

    # Build a table containing the number of sessions per animal/task.
    session_counts = (
        pd.DataFrame(
            {
                task_type: {
                    animal_id: len(data[animal_id].get(task_type, []))
                    for animal_id in animal_ids
                }
                for task_type in task_types
            },
            index=animal_ids,
        )
        .fillna(0)
        .astype(int)
    )

    if show_counts:
        plot_data = session_counts
        annotations = True
        colorbar_label = "Number of sessions"
        title = "Behavioral sessions per animal and task type"
    else:
        plot_data = (session_counts > 0).astype(int)
        annotations = plot_data.replace(
            {
                1: "✓",
                0: "",
            }
        )
        colorbar_label = None
        title = "Task types run for each animal"

    # Set figure dimensions based on the number of animals and task types.
    fig, ax = plt.subplots(
        figsize=(
            max(8, len(task_types) * 1.2),
            max(4, len(animal_ids) * 0.35),
        )
    )

    sns.heatmap(
        plot_data,
        annot=annotations,
        fmt="",
        cmap="Blues",
        vmin=0,
        vmax=None if show_counts else 1,
        linewidths=0.5,
        linecolor="white",
        cbar=show_counts,
        cbar_kws=({"label": colorbar_label} if show_counts else None),
        ax=ax,
    )

    ax.set_title(title)
    ax.set_xlabel("Task type")
    ax.set_ylabel("Animal ID")
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()
    plt.show()

    return fig, ax