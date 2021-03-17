# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 13:17:48 2021

@author: olehe
"""


import pandas as pd
import os.path

# Import GSA
import GSA
# this imports the functions used for getting information and preview-mp3s.

# multiprocessing for improved speeed
from joblib import Parallel, delayed

# tqdm for progressbar
from tqdm import tqdm


#%% Initiate GSA and authenticate

GSA.authenticate()



# 

GSA.sp.current_user_recently_played()