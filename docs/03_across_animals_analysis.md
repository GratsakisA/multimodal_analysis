# 03_across_animals_analysis

**Notebook:** [`03_across_animals_analysis.ipynb](../notebooks/03_across_animals_analysis.ipynb)

## General aim

The general aim of this notebook should be described in an `## Aim` section.

This notebook is part of the behavioral/multimodal analysis workflow. It is used to process, inspect, or analyze experimental data according to the task described above.

## Notebook structure

- Across animals analysis

The sections above follow the order in which the analysis is performed in the notebook.

## Functions used

### `create_analysis_key(animal_id, from_session, to_session, difficulties, excluded_sessions)`

**Defined in:** `src/multimodal_analysis/config/key_config.py`

**Purpose:** Create a configuration dictionary for an analysis.

**Usage:**

Use `create_analysis_key()` in the notebook to perform this operation.

**Example:**

```python
animal_configs = {
    299: {
        "from_session": 100,
        "to_session": 333,
        "difficulties": [2],
        "excluded_sessions": [],
    },
    288: {
        "from_session": 184,
        "to_session": 369,
        "difficulties": [2],
        "excluded_sessions": [],
    },
    324: {
        "from_session": 47,
        "to_session": 93,
        "difficulties": [2],
        "excluded_sessions": [],
    },
    326: {
        "from_session": 57,
        "to_session": 100,
        "difficulties": [2],
        "excluded_sessions": [],
    },
    328: {
        "from_session": 105,
        "to_session": 165,
        "difficulties": [2],
        "excluded_sessions": [],
    },
    410: {
        "from_session": 135,
        "to_session": 196,
        "difficulties": [2],
        "excluded_sessions": [],
    },
}

keys = [
    create_analysis_key(
        animal_id=animal_id,
        from_session=config["from_session"],
        to_session=config["to_session"],
        difficulties=config["difficulties"],
        excluded_sessions=config["excluded_sessions"],
    )
    for animal_id, config in animal_configs.items()
]
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `get_behavior_sessions(animal_id=None, task_type=None)`

**Defined in:** `src/multimodal_analysis/config/beh_sessions.py`

**Purpose:** Get behavioral sessions filtered by animal and task type.

**Usage:**

Use `get_behavior_sessions()` in the notebook to perform this operation.

**Example:**

```python
# Get the behavioral sessions available for the selected animal and task.
sessions_idx = get_behavior_sessions(animal_id=animal_id, task_type=task_type)
print("sessions_idx: \n", sessions_idx)

# Define the first session to include in the analysis.
from_session = get_behavior_sessions(animal_id=animal_id, task_type=task_type)[0]
print("\nfrom_session:", from_session)

# Define the last session to include in the analysis.
to_session = get_behavior_sessions(animal_id=animal_id, task_type=task_type)[-75]
print("to_session:", to_session)

# Calculate the total number of sessions included in the analysis.
total_sessions = sum(from_session <= session <= to_session for session in sessions_idx)
print("total_sessions:", total_sessions)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `get_schema_modules()`

**Defined in:** `src/multimodal_analysis/db/config.py`

**Purpose:** Initialize and return all schemas as individual modules.

**Usage:**

Use `get_schema_modules()` in the notebook to perform this operation.

**Example:**

```python
from multimodal_analysis.db import get_schema_modules

exp, stim, beh, inter, rec, mice = get_schema_modules()

from multimodal_analysis.config import (
    create_analysis_key,
    get_behavior_sessions,
    plot_behavior_task_types,
)
from multimodal_analysis.plots import (
    plot_modalities_across_animals_scatter,
    plot_modalities_across_animals_line,
)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `plot_behavior_task_types(show_counts=False)`

**Defined in:** `src/multimodal_analysis/config/beh_sessions.py`

**Purpose:** Plot which behavioral task types have been run for each animal.

Args:
    show_counts (bool, optional):
        If True, display the number of sessions per task type.
        If False, display task-type presence or absence.
        Defaults to False.

Returns:
    tuple: Matplotlib figure and axes.

**Usage:**

Use `plot_behavior_task_types()` in the notebook to perform this operation.

**Example:**

```python
# Plot behavioral task types across animals.
# Parameter:
# show_counts (bool): If True, display the number of sessions per task type.
task_type_across_animals = plot_behavior_task_types(show_counts=True)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `plot_modalities_across_animals_scatter(keys, stim, exp)`

**Defined in:** `src/multimodal_analysis/plots/across_animals.py`

**Purpose:** Plot performance comparisons across sensory modalities for multiple animals.

Creates four scatter plots comparing auditory, visual, and
multimodal performance across animals and sessions.

Args:
    keys (list[dict]): Analysis configurations, one per animal.
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.

Returns:
    pd.DataFrame: Combined performance data across animals.

**Usage:**

Use `plot_modalities_across_animals_scatter()` in the notebook to perform this operation.

**Example:**

```python
plot_modalities_across_animals_scatter(keys, stim, exp)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.
