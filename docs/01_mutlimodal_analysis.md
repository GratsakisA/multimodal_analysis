# 01_mutlimodal_analysis

**Notebook:** [`01_mutlimodal_analysis.ipynb](../notebooks/01_mutlimodal_analysis.ipynb)

## General aim

The general aim of this notebook should be described in an `## Aim` section.

This notebook is part of the behavioral/multimodal analysis workflow. It is used to process, inspect, or analyze experimental data according to the task described above.

## Notebook structure

- Multimodal Analysis
  - Purpose
  - Available Functions

The sections above follow the order in which the analysis is performed in the notebook.

## Functions used

### `create_analysis_key(animal_id, from_session, to_session, difficulties, excluded_sessions)`

**Defined in:** `src/multimodal_analysis/config/key_config.py`

**Purpose:** Create a configuration dictionary for an analysis.

**Usage:**

Use `create_analysis_key()` in the notebook to perform this operation.

**Example:**

```python
# Create the analysis configuration for the selected animal and sessions.
# Parameters:
# animal_id (int): Animal ID.
# from_session (int): First session.
# to_session (int): Last session.
# difficulties (list): Difficulty levels to include.
# excluded_sessions (list): Sessions to exclude.
key = create_analysis_key(
    animal_id, from_session, to_session, difficulties, excluded_sessions
)
print(key)
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
from_session = get_behavior_sessions(animal_id=animal_id, task_type=task_type)[10]
print("\nfrom_session:", from_session)

# Define the last session to include in the analysis.
to_session = get_behavior_sessions(animal_id=animal_id, task_type=task_type)[-1]
print("to_session:", to_session)

# Calculate the total number of sessions included in the analysis.
total_sessions = len(sessions_idx[:])
print("total_sessions:", total_sessions)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `get_linePlot_per_modality_across_sessions(animal_id, from_session, to_session, stim, exp, excluded_sessions, difficulties, criterion=0.65)`

**Defined in:** `src/multimodal_analysis/plots/modality.py`

**Purpose:** Plot performance across sessions for each modality.

Creates a line plot showing performance trajectory for auditory, visual,
multimodal, and difficult variants across sessions.

Args:
    animal_id (str): Animal identifier.
    from_session (int): Start session number (inclusive).
    to_session (int): End session number (inclusive).
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    excluded_sessions (list or set): Session numbers to exclude.
    difficulties (int or list): Difficulty level(s) to include.
    criterion (float, optional): Performance criterion line.
        Defaults to 0.65 (65%).
    
Returns:
    None: Displays plot using plt.show().
    
Example:
    >>> get_linePlot_per_modality_across_sessions(
    ...     'mouse_1', 1, 20, stim, exp, set(), [1, 2], criterion=0.65
    ... )

**Usage:**

Use `get_linePlot_per_modality_across_sessions()` in the notebook to perform this operation.

**Example:**

```python
# Plot performance across sessions for each modality
# Parameters:
# key (dict), stim (stimulus schema), exp (experiment schema), criterion (float)
get_linePlot_per_modality_across_sessions(key, stim, exp, criterion=0.65)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `get_scatter_plot_modalities(animal_id, from_session, to_session, stim, exp, excluded_sessions, difficulties)`

**Defined in:** `src/multimodal_analysis/plots/modality.py`

**Purpose:** Plot scatter comparison of performance between modalities.

Creates four scatter plots comparing performance between different
modality pairs with diagonal reference lines.

Args:
    animal_id (str): Animal identifier.
    from_session (int): Start session number (inclusive).
    to_session (int): End session number (inclusive).
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    excluded_sessions (list or set): Session numbers to exclude.
    difficulties (int or list): Difficulty level(s) to include.
    
Returns:
    None: Displays plot using plt.show().
    
Example:
    >>> get_scatter_plot_modalities(
    ...     'mouse_1', 1, 20, stim, exp, set(), [1, 2]
    ... )

**Usage:**

Use `get_scatter_plot_modalities()` in the notebook to perform this operation.

**Example:**

```python
# Plot performance comparisons across sensory modalities
# Parameters:
# key (dict), stim (stimulus schema), exp (experiment schema)
get_scatter_plot_modalities(key, stim, exp)
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

from multimodal_analysis.config import create_analysis_key, get_behavior_sessions
from multimodal_analysis.plots import (
    get_linePlot_per_modality_across_sessions,
    get_scatter_plot_modalities,
)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.
