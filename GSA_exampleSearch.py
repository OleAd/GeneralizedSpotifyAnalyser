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

results = GSA.searchPlaylists('Corona', number=50, market=None)

# The spotify API limits playlist searches to 1000.

#%% add the number of followers to the dataframe using the GSA.getPlaylistFollowers() function

followers = GSA.getPlaylistFollowers(results['playlistID'])

# and now merge them

# merge with original dataset to get supplementary information	
results = results.merge(followers, on ='playlistID', how='left')

