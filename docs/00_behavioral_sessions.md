# 00_behavioral_sessions

**Notebook:** [`00_behavioral_sessions.ipynb](../notebooks/00_behavioral_sessions.ipynb)

## General aim

The general aim of this notebook should be described in an `## Aim` section.

This notebook is part of the behavioral/multimodal analysis workflow. It is used to process, inspect, or analyze experimental data according to the task described above.

## Notebook structure

- Behavioral sessions
  - Management of sessions
  - Quick Overview of Sessions

The sections above follow the order in which the analysis is performed in the notebook.

## Functions used

### `add_behavior_sessions(animal_id, task_type, sessions)`

**Defined in:** `src/multimodal_analysis/config/beh_sessions.py`

**Purpose:** Add behavioral sessions for an animal and task type.

**Usage:**

Use `add_behavior_sessions()` in the notebook to perform this operation.

**Example:**

```python
# Add the sessions to the behavioral session configuration.
add_behavior_sessions(animal_id=animal_id, task_type=task_type, sessions=sessions)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


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
# Retrieve and verify the sessions currently assigned
# to this animal and task type.
get_behavior_sessions(animal_id=animal_id, task_type=task_type)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `get_object_distribution_trials(key, stim, exp, incl_aborts=False)`

**Defined in:** `src/multimodal_analysis/plots/distribution.py`

**Purpose:** Return visual/audiovisual trial counts per object and session.

Each object has one column containing 'visual / audiovisual' counts.
Missing objects are represented as '0 / 0'.

Args:
    key (dict): Analysis configuration.
    stim: DataJoint stimuli schema.
    exp: DataJoint experiment schema.
    incl_aborts (bool): Whether to include aborted trials.

Returns:
    pd.DataFrame: One row per session and one column per object.

**Usage:**

Use `get_object_distribution_trials()` in the notebook to perform this operation.

**Example:**

```python
# Trial distribution dataframe of each object across sessions
# Parameters:
# key (dict): animal_id, from_session, to_session, difficulties, excluded_sessions
# incl_aborts (bool): Whether to include aborted trials.
# Returns:
# Formatted DataFrame with highlighted object trial counts:
#   - Light green: Trials are present in both visual and audiovisual modalities.
#   - Orange: Trials are present in only one modality.
#   - No color: No trials are present in either modality (0 / 0).
get_object_distribution_trials(key, stim, exp, incl_aborts=False).style.map(
    highlight_object_trials_distribution_table
)
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
from multimodal_analysis.db import get_schema_modules, get_schemas

exp, stim, beh, inter, rec, mice = get_schema_modules()

from multimodal_analysis.config import (
    add_behavior_sessions,
    get_behavior_sessions,
    remove_behavior_sessions,
    create_analysis_key
)

from multimodal_analysis.plots import (
    # distribution.py
    get_condition_distribution_data,
    plot_condition_trial_distribution,
    plot_condition_distribution_percentage,
    get_object_distribution_trials, highlight_object_trials_distribution_table,
    # modality.py
    get_linePlot_per_modality_across_sessions,
    get_scatter_plot_modalities,
    # multimodal_trials.py
    get_multimodal_performance_summary,
    plot_multimodal_performance_per_object,
    # responses.py
    calculate_response_type,
    plot_response_counts,
    # visual_trials.py
    get_visual_performance_summary,
    plot_visual_performance_per_object
)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `plot_condition_distribution_percentage(key, stim, exp, incl_aborts=False)`

**Defined in:** `src/multimodal_analysis/plots/distribution.py`

**Purpose:** Plot trial distribution as percentage across conditions.

Creates a horizontal stacked bar chart showing the percentage of trials
in each condition for each session.

Args:
    key (dict): Analysis key with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session)
        - difficulties (list): Difficulty levels to include
        - excluded_sessions (set): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    incl_aborts (bool, optional): Include abort trials. Defaults to False.
    
Returns:
    None: Displays plot using matplotlib.
    
Example:
    >>> key = {'animal_id': 'mouse_1', 'sessions': (1, 20), ...}
    >>> plot_condition_distribution_percentage(key, stim, exp)

**Usage:**

Use `plot_condition_distribution_percentage()` in the notebook to perform this operation.

**Example:**

```python
# Distribution of each trial type across sessions in percentage
# Parameters:
# key (dict): animal_id, from_session, to_session, difficulties, excluded_sessions
# incl_aborts (bool): Whether to include aborted trials.
plot_condition_distribution_percentage(key, stim, exp, incl_aborts=False)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `plot_condition_trial_distribution(key, stim, exp, incl_aborts=False)`

**Defined in:** `src/multimodal_analysis/plots/distribution.py`

**Purpose:** Plot trial counts across stimulus conditions.

Creates a grouped bar plot showing the number of trials per condition
for each session. Active conditions are displayed with separate bars.

Args:
    key (dict): Analysis key with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session)
        - difficulties (list): Difficulty levels to include
        - excluded_sessions (set): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    incl_aborts (bool, optional): Include abort trials. Defaults to False.
    
Returns:
    matplotlib.axes.Axes: The axes object containing the plot.
    
Example:
    >>> key = {'animal_id': 'mouse_1', 'sessions': (1, 20), ...}
    >>> ax = plot_condition_trial_distribution(key, stim, exp)
    >>> plt.show()

**Usage:**

Use `plot_condition_trial_distribution()` in the notebook to perform this operation.

**Example:**

```python
# Distribution of trial counts for each trial type across sessions.
# Parameters:
# key (dict): animal_id, from_session, to_session, difficulties, excluded_sessions
# incl_aborts (bool): Whether to include aborted trials.
plot_condition_trial_distribution(key, stim, exp, incl_aborts=False)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `remove_behavior_sessions(animal_id, task_type, sessions)`

**Defined in:** `src/multimodal_analysis/config/beh_sessions.py`

**Purpose:** Remove behavioral sessions for an animal and task type.

**Usage:**

Use `remove_behavior_sessions()` in the notebook to perform this operation.

**Example:**

```python
# Remove sessions from an animal and task type.
# Add the session IDs to the list below when removal is needed.
remove_behavior_sessions(animal_id=0, task_type="visual", sessions=[20,21])
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.
