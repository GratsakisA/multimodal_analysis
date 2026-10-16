# 02_stimulus_level_analysis

**Notebook:** [`02_stimulus_level_analysis.ipynb](../notebooks/02_stimulus_level_analysis.ipynb)

## General aim

The general aim of this notebook should be described in an `## Aim` section.

This notebook is part of the behavioral/multimodal analysis workflow. It is used to process, inspect, or analyze experimental data according to the task described above.

## Notebook structure

- Stimulus-level Analysis
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


### `get_auditory_performance_summary(key, stim, exp, pulse_freq='all')`

**Defined in:** `src/multimodal_analysis/plots/auditory_trials.py`

**Purpose:** Fetch and display auditory performance data in Jupyter.

Retrieves auditory performance for continuous and/or pulsed tones
and displays them as formatted tables in the notebook.

Args:
    key (dict): Analysis key dictionary with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session) range
        - difficulties (int or list): Difficulty level(s)
        - excluded_sessions (set, optional): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    pulse_freq (str or int, optional): Which tone types to display.
        - 'all': Display both continuous and pulsed (default)
        - 0: Display only continuous tone (0 Hz)
        - 100: Display only pulsed tone (100 Hz)
    
Returns:
    tuple: (pulse0_df, pulse100_df) DataFrames.
    
Raises:
    ValueError: If pulse_freq is not 'all', 0, or 100.
    
Example:
    >>> key = {'animal_id': 'mouse_1', 'sessions': (1, 20), 'difficulties': [1, 2]}
    >>> p0, p100 = get_auditory_performance_summary(key, stim, exp, pulse_freq='all')

**Usage:**

Use `get_auditory_performance_summary()` in the notebook to perform this operation.

**Example:**

```python
# Create a DataFrame summarizing auditory performance for each tone pulse frequency across sessions.
# Includes: performance, rewarded, punished, and aborted trials; valid trials; and tone pulse frequency.
# Parameters:
# key (dict), stim (Stimulus schema), exp (Experiment schema), 
# pulse_freq (str or int): "all", 100, or 0
aud_perf_df = get_auditory_performance_summary(key, stim, exp, pulse_freq="all")
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
to_session = get_behavior_sessions(animal_id=animal_id, task_type=task_type)[-1]
print("to_session:", to_session)

# Calculate the total number of sessions included in the analysis.
total_sessions = len(sessions_idx[:])
print("total_sessions:", total_sessions)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `get_multimodal_performance_summary(key, stim, exp)`

**Defined in:** `src/multimodal_analysis/plots/multimodal_trials.py`

**Purpose:** Fetch and display multimodal performance data in Jupyter.

Retrieves multimodal performance DataFrames for each object and displays
them as formatted tables in the notebook. Multimodal trials contain both
auditory and visual stimulus components.

Args:
    key (dict): Analysis key dictionary with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session) range
        - difficulties (int or list): Difficulty level(s)
        - excluded_sessions (set, optional): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    
Returns:
    dict: Dictionary mapping object_id to pd.DataFrame, or empty dict
          if no data found.
          
Example:
    >>> key = {
    ...     'animal_id': 'mouse_1',
    ...     'sessions': (1, 20),
    ...     'difficulties': [1, 2, 3]
    ... }
    >>> object_dfs = get_multimodal_performance_summary(key, stim, exp)

**Usage:**

Use `get_multimodal_performance_summary()` in the notebook to perform this operation.

**Example:**

```python
# Create a DataFrame summarizing multimodal performance for each object across sessions.
# Includes: session_trials, obj_perf (performance), obj_rew (rewarded trials)
# obj_pun (punished trials), valid_obj_trials, obj_abrt (aborted trials), obj_pct (object percentage)
# Parameters:
# key (dict), stim (Stimulus schema), exp (Experiment schema)
multi_perf_df = get_multimodal_performance_summary(key,stim,exp)
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
    get_auditory_performance_summary,
    get_multimodal_performance_summary,
    get_visual_performance_summary,
    plot_auditory_performance_per_frequency,
    plot_multimodal_performance_per_object,
    plot_visual_performance_per_object,
)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `get_visual_performance_summary(key, stim, exp)`

**Defined in:** `src/multimodal_analysis/plots/visual_trials.py`

**Purpose:** Fetch and display visual performance data in Jupyter.

Retrieves visual performance DataFrames for each object and displays
them as formatted tables in the notebook.

Args:
    key (dict): Analysis key dictionary with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session) range
        - difficulties (int or list): Difficulty level(s)
        - excluded_sessions (set, optional): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    
Returns:
    dict: Dictionary mapping object_id to pd.DataFrame, or empty dict
          if no data found.
          
Example:
    >>> key = {
    ...     'animal_id': 'mouse_1',
    ...     'sessions': (1, 20),
    ...     'difficulties': [1, 2, 3]
    ... }
    >>> object_dfs = get_visual_performance_summary(key, stim, exp)

**Usage:**

Use `get_visual_performance_summary()` in the notebook to perform this operation.

**Example:**

```python
# Create a DataFrame summarizing visual performance for each object across sessions.
# Includes: session_trials, obj_perf, obj_rew (rewarded trials)
# obj_pun (punished trials), valid_obj_trials, obj_abrt (aborted trials), obj_pct (object percentage)
# Parameters:
# key (dict), stim (Stimulus schema), exp (Experiment schema)
visual_perf_df = get_visual_performance_summary(key,stim,exp)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `plot_auditory_performance_per_frequency(key, stim, exp, criterion=0.65)`

**Defined in:** `src/multimodal_analysis/plots/auditory_trials.py`

**Purpose:** Plot auditory performance by tone frequency.

Creates two subplots: a line plot showing performance trajectory for each
tone type across sessions, and a bar plot with 95% confidence intervals
for mean performance by tone frequency.

Args:
    key (dict): Analysis key dictionary with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session) range
        - difficulties (int or list): Difficulty level(s)
        - excluded_sessions (set, optional): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    criterion (float, optional): Performance criterion line.
        Defaults to 0.65 (65%).
    
Returns:
    None: Displays plot using plt.show().
    
Example:
    >>> plot_auditory_performance_per_frequency(key, stim, exp, criterion=0.65)

**Usage:**

Use `plot_auditory_performance_per_frequency()` in the notebook to perform this operation.

**Example:**

```python
# Plot auditory performance across sessions and mean performance per tone pulse frequency, with 95% confidence intervals.
# Parameters:
# key (dict), stim (stimulus schema), exp (experiment schema), criterion (float)
plot_auditory_performance_per_frequency(key, stim, exp, criterion=0.65)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `plot_multimodal_performance_per_object(key, stim, exp, criterion=0.65)`

**Defined in:** `src/multimodal_analysis/plots/multimodal_trials.py`

**Purpose:** Plot multimodal performance across objects and sessions.

Creates two subplots: a line plot showing performance trajectory across
sessions for each object, and a bar plot with 95% confidence intervals
for mean performance. Includes criterion line and sample size annotations.

Args:
    key (dict): Analysis key dictionary with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session) range
        - difficulties (int or list): Difficulty level(s)
        - excluded_sessions (set, optional): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    criterion (float, optional): Performance criterion line.
        Defaults to 0.65 (65%).
    
Returns:
    None: Displays plot using plt.show().
    
Example:
    >>> plot_multimodal_performance_per_object(key, stim, exp, criterion=0.65)

**Usage:**

Use `plot_multimodal_performance_per_object()` in the notebook to perform this operation.

**Example:**

```python
# Plot multimodal performance across sessions and mean performance per object, with 95% confidence intervals.
# Parameters:
# key (dict), stim (stimulus schema), exp (experiment schema), criterion (float)
multi_perf_plot = plot_multimodal_performance_per_object(key,stim,exp,criterion=0.65)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.


### `plot_visual_performance_per_object(key, stim, exp, criterion=0.65)`

**Defined in:** `src/multimodal_analysis/plots/visual_trials.py`

**Purpose:** Plot visual performance across objects and sessions.

Creates two subplots: a line plot showing performance trajectory across
sessions, and a bar plot with 95% confidence intervals for mean performance.
Includes criterion line and sample size annotations.

Args:
    key (dict): Analysis key dictionary with keys:
        - animal_id (str): Animal identifier
        - sessions (tuple): (from_session, to_session) range
        - difficulties (int or list): Difficulty level(s)
        - excluded_sessions (set, optional): Sessions to exclude
    stim: DataJoint stimuli schema.
    exp: DataJoint experiments schema.
    criterion (float, optional): Performance criterion line. 
        Defaults to 0.65 (65%).
    
Returns:
    None: Displays plot using plt.show().
    
Example:
    >>> plot_visual_performance_per_object(key, stim, exp, criterion=0.65)

**Usage:**

Use `plot_visual_performance_per_object()` in the notebook to perform this operation.

**Example:**

```python
# Plot visual performance across sessions and mean performance per object, with 95% confidence intervals.
# Parameters:
# key (dict), stim (stimulus schema), exp (experiment schema), criterion (float)
visual_perf_plot = plot_visual_performance_per_object(key,stim,exp,criterion=0.65)
```

**Output:**

The function returns the result described by its implementation/docstring. See the function definition for details.
