# This task consists of five trial-types:
# audiovisual trials, unimodal visual trials, unimodal auditory trials, unimodal challenged visual trials, and challenged multimodal trials.
# visual stimuli: 212, 213, 218, 219 & 214, 217 ("difficult stimuli")
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

# Difficulty 3
block = exp.Block(
    difficulty=3, 
    next_up=3, 
    next_down=3, 
    staircase_window=30,
    trial_selection='staircase', 
    stair_up=0.75, 
    stair_down=0.55
)


reward_amount = 6
tone_volume = 15
obj_mag = 0.5

# Multimodal condition 
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
            # visual parameters
            'obj_id'              : resp_obj[idx],
            'obj_dur'             : 9000,
            'obj_pos_x'           : 0, 
            'obj_pos_y'           : 0.02, 
            'obj_mag'             : obj_mag,              
            'obj_rot'             : (rots, rots),     
            'obj_tilt'            : (0,0),            
            # auditory parameters
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : tone_volume,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]],
            # response parameters
            'reward_port'         : rew_prob[idx], 
            'response_port'       : rew_prob[idx], 
            'reward_amount'       : reward_amount
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
             # visual parameters
            'obj_id'              : resp_obj[idx],
            'obj_dur'             : 9000,
            'obj_pos_x'           : 0, 
            'obj_pos_y'           : 0.02, 
            'obj_mag'             : obj_mag,              
            'obj_rot'             : (rots, rots),     
            'obj_tilt'            : (0,0),            
            # auditory parameters
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : 0,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]],
            # response parameters
            'reward_port'         : rew_prob[idx], 
            'response_port'       : rew_prob[idx], 
            'reward_amount'       : reward_amount
        }
    )

# Auditory condition 
aud_cond = []

resp_obj = [219,212]      
rew_prob = [1,2]       
tone_pulse_freq = [0,100]

rot_f = lambda: interp((np.random.rand(20)-.5) *100)
rots = rot_f() 

for idx, obj_comb in enumerate(resp_obj):
    aud_cond += exp.make_conditions(
        stim_class=panda_obj, 
        conditions={
            **env_key, 
            **block.dict(),
            # visual parameters
            'obj_id'              : resp_obj[idx],
            'obj_dur'             : 9000,
            'obj_pos_x'           : 0, 
            'obj_pos_y'           : 0.02, 
            'obj_mag'             : 0,              
            'obj_rot'             : (rots, rots),     
            'obj_tilt'            : (0,0),            
            # auditory parameters
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : tone_volume,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]],
            # response parameters
            'reward_port'         : rew_prob[idx], 
            'response_port'       : rew_prob[idx], 
            'reward_amount'       : reward_amount
        }
    )

# Difficult unimodal-visual morphs (obj_id: 217, 214)
vis_dif_cond = []

resp_obj = [217,214]      
rew_prob = [1,2]       
tone_pulse_freq = [0,100]

rot_f = lambda: interp((np.random.rand(20)-.5) *100)
rots = rot_f() 

for idx, obj_comb in enumerate(resp_obj):
    vis_dif_cond += exp.make_conditions(
        stim_class=panda_obj, 
        conditions={
            **env_key, 
            **block.dict(),
            # visual parameters
            'obj_id'              : resp_obj[idx],
            'obj_dur'             : 9000,
            'obj_pos_x'           : 0, 
            'obj_pos_y'           : 0.02, 
            'obj_mag'             : obj_mag,              
            'obj_rot'             : (rots, rots),     
            'obj_tilt'            : (0,0),            
            # auditory parameters
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : 0,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]],
            # response parameters
            'reward_port'         : rew_prob[idx], 
            'response_port'       : rew_prob[idx], 
            'reward_amount'       : reward_amount
        }
    )
    
# Difficult multimodal morphs (obj_id: 217, 214) 
multi_dif_cond = []

resp_obj = [217,214]      
rew_prob = [1,2]       
tone_pulse_freq = [0,100]

rot_f = lambda: interp((np.random.rand(20)-.5) *100)
rots = rot_f() 

for idx, obj_comb in enumerate(resp_obj):
    multi_dif_cond += exp.make_conditions(
        stim_class=panda_obj, 
        conditions={
            **env_key, 
            **block.dict(),
            # visual parameters
            'obj_id'              : resp_obj[idx],
            'obj_dur'             : 9000,
            'obj_pos_x'           : 0, 
            'obj_pos_y'           : 0.02, 
            'obj_mag'             : obj_mag,              
            'obj_rot'             : (rots, rots),     
            'obj_tilt'            : (0,0), 
            # auditory parameters
            'tone_duration'       : 9000,
            'tone_frequency'      : 40500,
            'tone_volume'         : tone_volume,
            'tone_pulse_freq'     : [tone_pulse_freq[idx]],
            # response parameters
            'reward_port'         : rew_prob[idx], 
            'response_port'       : rew_prob[idx], 
            'reward_amount'       : reward_amount
        }
    )
    
# shuffle conditions
conditions = multi_cond + multi_cond + multi_cond + visual_cond + aud_cond + aud_cond + vis_dif_cond + multi_dif_cond

# Generate 24 conditions: 12 multi_cond, 4 visual_cond, 4 aud_cond, 2 vis_dif_cond and 2 multi_dif_cond
print(f"Total number of trials: {len(conditions)}")
print(f"Multimodal trials: {len(multi_cond) * 3}")
print(f"Visual trials: {len(visual_cond)}")
print(f"Auditory trials: {len(aud_cond) * 2}")
print(f"no_stim_reward: {len(vis_dif_cond)}")
print(f"no_stim_punish: {len(multi_dif_cond)}")

# run experiments
exp.push_conditions(conditions)
exp.start()