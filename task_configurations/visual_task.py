# This task consists of unimodal visual trials.
# visual stimuli: 212, 213, 218, 219 & 214, 217

from ethopy.experiments.match_port import Experiment
from ethopy.behaviors.multi_port import MultiPort
from ethopy.stimuli.panda import Panda
from scipy import interpolate
import time
import random
import numpy as np
from datetime import datetime


interp = lambda x: interpolate.splev(np.linspace(0, len(x), 100),
                            interpolate.splrep(np.linspace(0, len(x), len(x)), x)) if len(x) > 3 else x


# define session parameters
session_params = {
    'setup_conf_idx'        : 1, 
    'max_reward'            : 1200,
    'min_reward'            : 700,
    'hydrate_delay'         : 30,
}

exp = Experiment()
exp.setup(logger, MultiPort, session_params)

conditions = []

# define environment conditions
env_key = {
    # Experimental parameters
    'abort_duration'        : 500,
    'punish_duration'       : 10000,
    'init_ready'            : 50,
    'trial_ready'           : 100,
    'intertrial_duration'   : 500,
    'trial_duration'        : 9000,
    'reward_duration'       : 5000
    }

print(env_key)

panda_obj = Panda()
panda_obj.fill_colors.set({
    'background' : (0, 0, 0),
    'start'      : (0.2, 0.2, 0.2),
    'reward'     : (0.6, 0.6, 0.6),
    'punish'     : (0, 0, 0)
})


# Difficulty 1

resp_obj = [218,219,212,213]      
rew_prob = [1,1,2,2]         

rot_f = lambda: interp((np.random.rand(20)-.5) *100)
rots = rot_f() # rotation of the object 

block = exp.Block(
    difficulty=1, 
    next_up=1, 
    next_down=1, 
    staircase_window=30,
    trial_selection='staircase', 
    stair_up=0.75, 
    stair_down=0.55, 
) 

for idx, obj_comb in enumerate(resp_obj):
  conditions += exp.make_conditions(
      stim_class=panda_obj, 
      conditions={
          **env_key, 
          **block.dict(),                                               
          'obj_id'              : resp_obj[idx],
          'obj_dur'             : 9000,
          'obj_pos_x'           : 0,
          'obj_pos_y'           : 0.02,
          'obj_mag'             : 0.5,              # size of the object
          'obj_rot'             : (rots, rots),     # rotation of the object
          'obj_tilt'            : (0,0),            # tilt of the object
          'reward_port'         : rew_prob[idx], 
          'response_port'       : rew_prob[idx], 
          'reward_amount'       : 6,
      }
  )


seed_value = int(datetime.now().strftime("%Y%m%d"))
# seed_value = int(datetime.now().timestamp()) % (2**32)
np.random.seed(seed_value)

# run experiments
exp.push_conditions(conditions)
exp.start()