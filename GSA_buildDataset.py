# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 13:47:26 2021

@author: olehe

This example script shows how to quickly build a dataset
"""

#%% Do imports

import pandas as pd

# Import GSA
import GSA
# this imports the functions used for getting information and preview-mp3s.

# multiprocessing for improved speeed
from joblib import Parallel, delayed

# tqdm for progressbar
from tqdm import tqdm




#%% Initiate GSA and authenticate

GSA.authenticate()


#%% Build our dataset

# search for Finnish Metal playlists
finnishMetal = GSA.searchPlaylists('Finnish Metal', number=400, market='FI')
# currently yields 142 playlists

# search for Norwegian Metal playlists
norwegianMetal = GSA.searchPlaylists('Norwegian Metal', number=400, market='NO')
# currently yields 165 playlists


# check for duplicates
finnishMetal = finnishMetal.drop_duplicates(subset=['playlistID'])
norwegianMetal = norwegianMetal.drop_duplicates(subset=['playlistID'])


# Select only playlists with over 20 tracks
finnishMetal = finnishMetal[finnishMetal['nTracks'] > 20]
norwegianMetal = norwegianMetal[norwegianMetal['nTracks'] > 20]

# add category
finnishMetal['category'] = 'Finnish'
norwegianMetal['category'] = 'Norwegian'

# merge into one dataframe
playlists_dataset = pd.concat([finnishMetal, norwegianMetal], ignore_index=True)

# save for posterity
# playlists_dataset.to_csv('Data/metal_dataset_playlistsOnly.csv', encoding='UTF-8')


#%% Get tracks

#uncomment to load previously saved dataset
playlists_dataset = pd.read_csv('Data/metal_dataset_playlistsOnly.csv', encoding='UTF-8', na_values='', index_col=0)



IDlist_tqdm = tqdm(playlists_dataset['playlistID'], desc='Getting audio features') 
results = Parallel(n_jobs=2, require='sharedmem')(delayed(GSA.getInformation)(thisList) for thisList in IDlist_tqdm)
# set n_jobs to as many threads you want your to use on your cpu.


#%% Add the supplementary information to the dataframe

# first collect all the playlists, as not all might have been successfully downloaded
output=[]
for thisList in results:
	if thisList == 'error':
		print('Found a playlist not downloaded.')
	else:
		thisFrame = pd.read_pickle(thisList)
		output.append(thisFrame)
	
# flatten
output = pd.concat(output)

# remove any where TrackName is EMPTYDATAFRAME
empties = output[output['TrackName'] == 'EMPTYDATAFRAME']
output.drop(empties.index, inplace=True)

# merge with original dataset to get supplementary information	
merged_output = playlists_dataset.merge(output, on ='playlistID', how='left')

# save output
merged_output.to_csv('Data/metal_dataset_allTracks.csv', encoding='UTF-8')

# now get rid of duplicate tracks

merged_output_unique = merged_output.drop_duplicates(subset=['TrackID', 'category'])
# save the unique tracks

merged_output_unique.to_csv('Data/metal_dataset_uniqueTracks.csv', encoding='UTF-8')
