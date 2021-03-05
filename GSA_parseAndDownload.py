# -*- coding: utf-8 -*-
"""
@author: Ole Adrian Heggli

This script takes a csv with Spotify Playlist IDs
Then gets all tracks from those playlists
Then gets audio features for those tracks
Then downloads a 30-second preview mp3.

"""



#%% Do imports

import pandas as pd
import time
import os.path
import random
import requests

# Import spotify
import spotipy
import spotipy.oauth2 as oauth2


# Import credentials
import spotifyConstants
# this import contains client ID, Secret, and redirect URL
# for the script to work, you need to make one yourself using the Spotify Developer system

# multiprocessing for improved speeed
from joblib import Parallel, delayed

# tqdm for progressbar
from tqdm import tqdm




#%% Initiate spotipy
# This initiates a token allowing you to access the Spotify API

sp_oauth = oauth2.SpotifyOAuth(client_id=spotifyConstants.myClientID,
							   client_secret=spotifyConstants.myClientSecret,
							   redirect_uri=spotifyConstants.myRedirect,
							   scope=None, cache_path='/.cache')


# this function checks of the token is expired, and refreshes it if so 
# Call this before every call to sp.
def refresh():
	global token_info, sp
	
	if sp_oauth.is_token_expired(token_info):
		token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
		token = token_info['access_token']
		sp = spotipy.Spotify(auth=token)



# need to rewrite this section, as currently you have to manually do it.
#token_info = sp_oauth.get_cached_token()
#if not token_info:
auth_url = sp_oauth.get_authorize_url()
print('\n')
print(auth_url)
print('\n')
# If the session hangs at this line, just paste the reponse manually into response.
response = input('Paste the above link into your browser, then paste the redirect url here: ')
code = sp_oauth.parse_response_code(response)

# Note a deprecation warning with this one. 
token_info = sp_oauth.get_access_token(code)

token = token_info['access_token']

sp = spotipy.Spotify(auth=token)



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

# Now get tracks out of the playlists
completedPlaylists=[]
totalTracks = 0


#%% Function for getting information
def getInformation(thisList):
	refresh()

	global sp

	column_names = ['playlistID','TrackName', 'TrackID', 'SampleURL', 'ReleaseYear', 'Genres', 'danceability', 'energy', 
				'loudness', 'speechiness', 'acousticness', 'instrumentalness',
				'liveness', 'valence', 'tempo', 'key', 'mode', 'duration_ms']
	sampleDataFrame = pd.DataFrame(columns = column_names)
	# Sleep a little bit to not piss of Spotify
	thisSleep = random.randint(0,10) * 0.08
	time.sleep(thisSleep)
	
	# make a filename to save it to
	# also, return this filename
	thisSaveName = 'Playlists/' + thisList + '.pkl'
	
	# now check if the file already exists
	if os.path.isfile(thisSaveName):
		return thisSaveName
	
	# refresh token
	refresh()
	try:
		theseTracks = sp.playlist_tracks(thisList, limit=None)
	except:
		# handle errors with getting tracks
		theseTracks = 0
		thisDict = [{'playlistID':'EMPTYDATAFRAME',
				 'TrackName':'EMPTYDATAFRAME',
				 'TrackID':'EMPTYDATAFRAME',
				 'SampleURL':'EMPTYDATAFRAME',
				 'ReleaseYear': 'EMPTYDATAFRAME',
				 'Genres':'EMPTYDATAFRAME',
				 'Popularity':-1,
				 'danceability':0,
				 'energy':0,
				 'loudness':0,
				 'speechiness':0,
				 'acousticness':0,
				 'instrumentalness':0,
				 'liveness':0,
				 'valence':0,
				 'tempo':0,
				 'key':0,
				 'mode':0,
				 'duration_ms':0
				 }]
		thisDf = pd.DataFrame(thisDict)
		sampleDataFrame = sampleDataFrame.append(thisDf, ignore_index=True)
		return thisSaveName
		

	# Make sure to get all tracks in a playlist
	tracks = theseTracks['items']
	while theseTracks['next']:
		theseTracks = sp.next(theseTracks)
		tracks.extend(theseTracks['items'])
	
	for track in tracks:
		if track['track']==None:
			continue
		thisId=track['track']['id']
		if thisId == None:
			continue
		thisName=track['track']['name']
		print(thisName)
		print('\n')
		
		thisReleaseDate = track['track']['album']['release_date']
		thisPopularity = track['track']['popularity']
		
		if thisPopularity == None:
			thisPopularity=-1
		
		if thisReleaseDate == None:
			thisReleaseDate = 0
			
		# genre is linked to artist, not to song. Therefore, need another get here.
		# first get artist.
		# will get the first artist, there might be numerous

		thisArtistId = track['track']['artists'][0]['id']
		if thisArtistId == None:
			thisGenres = '[unknown]'
		else:
			refresh()
			try:
				thisArtistInfo = sp.artist(thisArtistId)
				thisGenres = thisArtistInfo['genres']
			except:
				thisGenres = []
			if thisGenres == []:
				thisGenres = '[unknown]'
		
		
		thisUrl=track['track']['preview_url']
		# Sleep a little bit to avoid rate limiting
		thisSleep = random.randint(0,10)*0.09
		time.sleep(thisSleep)
		# Get audio features for the track
		refresh()
		thisFeature=sp.audio_features(tracks=thisId)
		
		# Create a dataframe entry
		if thisFeature[0]!=None:
			thisDict = [{'playlistID':thisList,
				 'TrackName':thisName,
				 'TrackID':thisId,
				 'SampleURL':thisUrl,
				 'ReleaseYear': thisReleaseDate,
				 'Genres':thisGenres,
				 'Popularity':thisPopularity,
				 'danceability':thisFeature[0]['danceability'],
				 'energy':thisFeature[0]['energy'],
				 'loudness':thisFeature[0]['loudness'],
				 'speechiness':thisFeature[0]['speechiness'],
				 'acousticness':thisFeature[0]['acousticness'],
				 'instrumentalness':thisFeature[0]['instrumentalness'],
				 'liveness':thisFeature[0]['liveness'],
				 'valence':thisFeature[0]['valence'],
				 'tempo':thisFeature[0]['tempo'],
				 'key':thisFeature[0]['key'],
				 'mode':thisFeature[0]['mode'],
				 'duration_ms':thisFeature[0]['duration_ms']
				 }]
			thisDf = pd.DataFrame(thisDict)
			sampleDataFrame = sampleDataFrame.append(thisDf, ignore_index=True)

	
	# do a check here to see if empty 
	if sampleDataFrame.empty:
		thisDict = [{'playlistID':'EMPTYDATAFRAME',
				 'TrackName':'EMPTYDATAFRAME',
				 'TrackID':'EMPTYDATAFRAME',
				 'SampleURL':'EMPTYDATAFRAME',
				 'ReleaseYear': 'EMPTYDATAFRAME',
				 'Genres':'EMPTYDATAFRAME',
				 'Popularity':-1,
				 'danceability':0,
				 'energy':0,
				 'loudness':0,
				 'speechiness':0,
				 'acousticness':0,
				 'instrumentalness':0,
				 'liveness':0,
				 'valence':0,
				 'tempo':0,
				 'key':0,
				 'mode':0,
				 'duration_ms':0
				 }]
		thisDf = pd.DataFrame(thisDict)
		sampleDataFrame = sampleDataFrame.append(thisDf, ignore_index=True)
		
	# save as pickle here
	sampleDataFrame.to_pickle(thisSaveName)
	return thisSaveName



#%% Get tracks
listsId = tqdm(IDlist, desc='Getting audio features') 
results = Parallel(n_jobs=8)(delayed(getInformation)(thisList) for thisList in listsId)
# set n_jobs to as many threads you want your to use on your cpu.


#%% Add the supplementary information to the dataframe
# first collect all the playlists, as not all might have been successfully downloaded

output=[]
for thisList in results:
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


#%% Function for downloading tracks
def downloadTracks(track):
	
	thisUrl = track[0]
	thisName = track[1]
	thisID = track[2]
	thisFolder = track[3]
	
	# Check if folder exist
	os.makedirs('Audio/' + thisFolder + '/', exist_ok=True)
	
	
	if thisUrl != None:
		time.sleep(random.randrange(0,42)/100)
		# maybe do a check if file exists here. Would need to move "thisname"
		try:
			thisSample = requests.get(thisUrl)
			if len(thisSample.content) > 0:
				# Clean up filename
				thisName = thisName.replace('/', '')
				thisName = thisName.replace('\\', '')
				thisName = thisName.replace('.', '')
				saveName = 'Audio/' + thisFolder + '/' + thisName + '_ID_' + thisID + '.mp3'
				saveName = saveName.replace(":", "")
				saveName = saveName.replace("!", "")
				saveName = saveName.replace('"', '')
				saveName = saveName.replace(":", "")
				saveName = saveName.replace("!", "")
				saveName = saveName.replace('"', '')
				saveName = saveName.replace('?', '')
				saveName = saveName.replace('<', '')
				saveName = saveName.replace('>', '')
				saveName = saveName.replace('\\', '')
				saveName = saveName.replace('*', '')
				saveName = saveName.replace('|', '')
				
				open(saveName, 'wb').write(thisSample.content)
				# add to database
				success = 1
		except:
			success = 0
	else:
		success = 0
	
	output = (thisID, success)
	
	
	return output



#%% Now download 30-sec preview mp3s

to_download = merged_output[['SampleURL', 'TrackName', 'TrackID', 'playlistID']].values.tolist()

to_download = tqdm(to_download, desc='Downloading tracks')
downloaded = Parallel(n_jobs=8)(delayed(downloadTracks)(track=thisTrack) for thisTrack in to_download)


#%% Now save a datafile containing only downloaded tracks
# Not all tracks have preview mp3's, this makes a dataframe containing only those successfully downloaded

downloaded_df = pd.DataFrame(downloaded, columns=['TrackID', 'Downloaded'])
downloadedKey = dict(zip(downloaded_df.TrackID, downloaded_df.Downloaded))

merged_output['Downloaded'] = 0
merged_output['Downloaded'] = merged_output['TrackID'].map(downloadedKey)

merged_output_downloaded = merged_output[merged_output['Downloaded'] == 1]
merged_output_downloaded.to_csv('Data/dataset_with_audiofeatures_downloaded.csv', encoding='UTF-8')




