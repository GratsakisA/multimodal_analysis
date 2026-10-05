# This task consists of multimodal trials (~50% of total trials) and unimodal visual (~25%) and auditory (~25%) trials.
# visual stimuli: 212, 213, 218, 219
# auditory stimuli: tone pulses 0 and 100 | tone_volume: 15

from ethopy.experiments.match_port import Experiment
from ethopy.behaviors.multi_port import MultiPort
from ethopy.stimuli.tones_panda import TonesPanda
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
    'abort_duration'        : 500,
    'punish_duration'       : 10000,
    'init_ready'            : 50,
    'trial_ready'           : 100,
    'intertrial_duration'   : 500,
    'trial_duration'        : 9000,
    'reward_duration'       : 5000
    }

print(env_key)

panda_obj = TonesPanda()
panda_obj.fill_colors.set({
    'background' : (0, 0, 0),
    'start'      : (0.2, 0.2, 0.2),
    'reward'     : (0.6, 0.6, 0.6),
    'punish'     : (0, 0, 0)
})

# Difficulty 2
block = exp.Block(
    difficulty=2, 
    next_up=2, 
    next_down=2, 
    staircase_window=30,
    trial_selection='staircase', 
    stair_up=0.75, 
    stair_down=0.55, 
) 

reward_amount = 6
tone_volume = 15

# multimodal condition 
multi_cond = []

resp_obj = [218,219,212,213]      
rew_prob = [1,1,2,2]       
tone_pulse_freq = [0,0,100,100]     

# rotation of the object 
rot_f = lambda: interp((np.random.rand(20)-.5) *100)
rots = rot_f() 

for idx, obj_comb in enumerate(resp_obj):
    multi_cond += exp.make_conditions(
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
            'reward_amount'       : reward_amount,
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : tone_volume,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]]
        }
    )

# Visual condition 
visual_cond = []

resp_obj = [218,219,212,213]      
rew_prob = [1,1,2,2]       
tone_pulse_freq = [0,0,100,100]     

rot_f = lambda: interp((np.random.rand(20)-.5) *100)
rots = rot_f() 

for idx, obj_comb in enumerate(resp_obj):
    visual_cond += exp.make_conditions(
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
            'reward_amount'       : reward_amount,
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : 0,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]]
        }
    )

# Auditory condition 
auditory_cond = []

resp_obj = [218,219,212,213]      
rew_prob = [1,1,2,2]       
tone_pulse_freq = [0,0,100,100]     

rot_f = lambda: interp((np.random.rand(20)-.5) *100)
rots = rot_f() 

for idx, obj_comb in enumerate(resp_obj):
    auditory_cond += exp.make_conditions(
        stim_class=panda_obj, 
        conditions={
            **env_key, 
            **block.dict(),
            'obj_id'              : resp_obj[idx],
            'obj_dur'             : 9000,
            'obj_pos_x'           : 0, 
            'obj_pos_y'           : 0.02, 
            'obj_mag'             : 0,      # <--------------- mag = 0 
            'obj_rot'             : (rots, rots),     # rotation of the object
            'obj_tilt'            : (0,0),            # tilt of the object
            'reward_port'         : rew_prob[idx], 
            'response_port'       : rew_prob[idx], 
            'reward_amount'       : reward_amount,
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : tone_volume,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]]
        }
    )

# shuffle conditions
conditions = multi_cond + multi_cond + multi_cond + visual_cond + auditory_cond 
random.shuffle(conditions)

# run experiments
exp.push_conditions(conditions)
exp.start()