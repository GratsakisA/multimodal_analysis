{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "bced6fcd-abb9-4571-96f2-b27272a06c0c",
   "metadata": {},
   "outputs": [],
   "source": [
    "import warnings\n",
    "warnings.filterwarnings('ignore')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "aa9e8a58-3540-4133-9832-bdc51085728a",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "✅ All imports successful!\n"
     ]
    }
   ],
   "source": [
    "import numpy as np\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "# Configure plotting\n",
    "sns.set_style(\"whitegrid\")\n",
    "plt.rcParams['figure.figsize'] = (12, 5)\n",
    "plt.rcParams['font.size'] = 10\n",
    "\n",
    "# Database\n",
    "from multimodal_analysis import get_schemas, SCHEMATA\n",
    "\n",
    "# Stimuli configuration\n",
    "from multimodal_analysis import (\n",
    "    DEFAULT_OBJECT_IDS,\n",
    "    OBJECT_ALIASES,\n",
    "    TONE_FREQUENCIES,\n",
    "    TONE_FREQUENCY_NAMES,\n",
    "    AUDITORY_TRIAL_CRITERIA,\n",
    "    MULTIMODAL_AUDITORY_CRITERIA\n",
    ")\n",
    "\n",
    "# Utilities\n",
    "from multimodal_analysis import validate_key, get_difficulties, fetch_sessions\n",
    "\n",
    "# Data fetching and computing\n",
    "from multimodal_analysis import (\n",
    "    fetch_visual_data,\n",
    "    fetch_multimodal_data,\n",
    "    compute_auditory_performance_summary,\n",
    "    compute_modality_performance\n",
    ")\n",
    "\n",
    "# Plotting\n",
    "from multimodal_analysis import (\n",
    "    plot_visual_performance_per_object,\n",
    "    plot_auditory_performance_per_frequency,\n",
    "    plot_multimodal_performance_per_object,\n",
    "    get_condition_distribution_data,\n",
    "    plot_condition_trial_distribution,\n",
    "    plot_condition_distribution_percentage,\n",
    "    get_linePlot_per_modality_across_sessions,\n",
    "    get_scatter_plot_modalities,\n",
    "    plot_response_counts\n",
    ")\n",
    "\n",
    "print(\"✅ All imports successful!\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "953fbb25-1bae-446c-a356-1f2684cb0221",
   "metadata": {},
   "outputs": [
    {
     "name": "stdin",
     "output_type": "stream",
     "text": [
      "Please enter DataJoint username:  eflab\n",
      "Please enter DataJoint password:  ········\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "[2026-10-05 13:02:00,115][INFO]: Connecting eflab@database.eflab.org:3306\n",
      "[2026-10-05 13:02:00,143][INFO]: Connected eflab@database.eflab.org:3306\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "✅ Database schemas loaded\n",
      "Available schemas: ['exp', 'stim', 'beh', 'inter', 'rec', 'mice']\n"
     ]
    }
   ],
   "source": [
    "# Cell 2: Initialize Database Schemas\n",
    "# ============================================================================\n",
    "# DATABASE INITIALIZATION\n",
    "# ============================================================================\n",
    "\n",
    "# Get all schemas\n",
    "schemas = get_schemas()\n",
    "\n",
    "# Extract individual schemas for easier access\n",
    "exp = schemas['exp']\n",
    "stim = schemas['stim']\n",
    "beh = schemas['beh']\n",
    "inter = schemas['inter']\n",
    "rec = schemas['rec']\n",
    "mice = schemas['mice']\n",
    "\n",
    "print(\"✅ Database schemas loaded\")\n",
    "print(f\"Available schemas: {list(schemas.keys())}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a103df5b-bd66-4d24-ba85-bb3e41c260a2",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
