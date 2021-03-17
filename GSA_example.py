# -*- coding: utf-8 -*-
"""
@author: Ole Adrian Heggli

This example script takes a csv with Spotify Playlist IDs
Then gets all tracks from those playlists
Then gets audio features for those tracks
Then downloads a 30-second preview mp3.

"""



#%% Do imports

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

#%% Parse csv-file
# The csv-file should as a minimum contain a column called playlistURI containing the playlist IDs

dataset = pd.read_csv('example_data.csv', low_memory=False, encoding='UTF-8', na_values='', index_col=False)

# Check that dataset contains "playlistURI"
if 'playlistURI' not in dataset.columns:
	print('WARNING: No playlistURI found in dataset.')


# Get playlistURI as list
URIlist = dataset.playlistURI.tolist()

# Strip the strings to get only the playlist ID
# Assume these are all the same length
loc_start = URIlist[0].find('/playlist/')

# Boil down to only the actual ID with length 22
IDlist = [playlist[loc_start+10:loc_start+10+22] for playlist in URIlist]

# Add the ID back to the original dataset for later lookup
dataset['playlistID'] = IDlist


# Make some folders if doesn't exist
if not os.path.exists('Playlists'):
	os.makedirs('Playlists')
if not os.path.exists('Audio'):
	os.makedirs('Audio')
if not os.path.exists('Data'):
	os.makedirs('Data')


#%% Get tracks
IDlist_tqdm = tqdm(IDlist, desc='Getting audio features') 
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
merged_output = dataset.merge(output, on ='playlistID', how='left')

# save output
merged_output.to_csv('Data/dataset_with_audiofeatures.csv', encoding='UTF-8')




#%% Now download 30-sec preview mp3s

to_download = merged_output[['SampleURL', 'TrackName', 'TrackID', 'playlistID']].values.tolist()
to_download = tqdm(to_download, desc='Downloading tracks')
downloaded = Parallel(n_jobs=8)(delayed(GSA.downloadTracks)(track=thisTrack) for thisTrack in to_download)


#%% Now save a datafile containing only downloaded tracks
# Not all tracks have preview mp3's, this makes a dataframe containing only those successfully downloaded

downloaded_df = pd.DataFrame(downloaded, columns=['TrackID', 'Downloaded'])
downloadedKey = dict(zip(downloaded_df.TrackID, downloaded_df.Downloaded))

merged_output['Downloaded'] = 0
merged_output['Downloaded'] = merged_output['TrackID'].map(downloadedKey)

merged_output_downloaded = merged_output[merged_output['Downloaded'] == 1]
merged_output_downloaded.to_csv('Data/dataset_with_audiofeatures_downloaded.csv', encoding='UTF-8')




