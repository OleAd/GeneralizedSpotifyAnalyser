# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 09:46:50 2021

@author: olehe

This script provides a simple overview of the GSA.searchPlaylist function
(which is a wrapper for Spotipy's search function)
"""
#%% Do imports

import pandas as pd

# Import GSA
import GSA

#%% Authenticate

GSA.authenticate()


#%% Do a search


# Let's do a search for corona music:
# Search term is 'Corona', we're searching up to 1k playlists, and in no specific market.

results = GSA.searchPlaylists('Corona', number=1000, market=None)

# The spotify API limits playlist searches to 1000.


