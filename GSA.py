# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 08:33:28 2021

This script contains functions used in the Generalized Spotify Analyser

@author: olehe

"""


# some general imports

import pandas as pd
import time
import math
import os.path
import random
import requests
import spotipy.oauth2 as oauth2
import spotipy


# Import credentials
import spotifyConstants

sp_oauth = oauth2.SpotifyOAuth(client_id=spotifyConstants.myClientID,
								   client_secret=spotifyConstants.myClientSecret,
								   redirect_uri=spotifyConstants.myRedirect,
								   username=spotifyConstants.myUser,
								   scope=None)

# create global sp? Not sure what is best, re parallelizing
# if global, then would need to update auth


sp = []

#%% Authenticate

def authenticate():
	#global token_info, sp_oauth, token
	global sp, sp_oauth
	sp = spotipy.Spotify(auth_manager=sp_oauth)
	
	# do a search to initiate
	not_output = sp.me()
	
	'''
	token_info = sp_oauth.get_cached_token()
	if not token_info:
		auth_url = sp_oauth.get_authorize_url()
		print('\n')
		print(auth_url)
		print('\n')
		# try to put the link in the clipboard
		pd.DataFrame([auth_url]).to_clipboard(index=False, header=False)
		
		
		# If the session hangs at this line, just paste the reponse manually into response.
		response = input('Paste the above link into your browser (it is in your clipboard), then paste the redirect url here: ')
		code = sp_oauth.parse_response_code(response)
		
		
		# Note a deprecation warning with this one. 
		token_info = sp_oauth.get_access_token(code)
		
	if sp_oauth.is_token_expired(token_info):
			token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
			token = token_info['access_token']
			print('Refreshed token')
	'''		
	#token = token_info['access_token']
	#global sp
	#sp = spotipy.Spotify(auth=token)
	return

#%% this function checks of the token is expired, and refreshes it if so 
# Call this before every call to sp.
def refresh():
	
	output = 0
	print('Refresh temporarily unstable. Working on fix.')
	'''
	token_info = sp_oauth.get_cached_token()
	if sp_oauth.is_token_expired(token_info):
			token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
			#token = token_info['access_token']
			print('Refreshed token')
			output = 1
	'''
	return output


#%% Function for getting information
def getInformation(thisList, verbose=False):
	# make a filename to save it to
	# also, return this filename
	global sp
	
	thisSaveName = 'Playlists/' + thisList + '.pkl'
	
	# now check if the file already exists
	if os.path.isfile(thisSaveName):
		return thisSaveName
	
	
	
	#refresh()

	if verbose:
		print('Getting audio features and information from playlist.')
	
	if not os.path.exists('Playlists'):
		os.makedirs('Playlists')

	'''
	#refresh()
	authenticate()
	token_info_cached = sp_oauth.get_cached_token()
	token_info = sp_oauth.refresh_access_token(token_info_cached['refresh_token'])
	token = token_info['access_token']
	sp = spotipy.Spotify(auth=token)
	'''
	

	column_names = ['playlistID','TrackName', 'TrackID', 'SampleURL', 'ReleaseYear', 'Genres', 'danceability', 'energy', 
				'loudness', 'speechiness', 'acousticness', 'instrumentalness',
				'liveness', 'valence', 'tempo', 'key', 'mode', 'duration_ms']
	sampleDataFrame = pd.DataFrame(columns = column_names)
	# Sleep a little bit to not piss of Spotify
	thisSleep = random.randint(0,10) * 0.01
	time.sleep(thisSleep)
	
	
	
	# refresh token
	#refresh()
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
		return 'error'
		

	# Make sure to get all tracks in a playlist
	tracks = theseTracks['items']
	while theseTracks['next']:
		#authenticate()
		theseTracks = sp.next(theseTracks)
		tracks.extend(theseTracks['items'])
	
	for track in tracks:
		if track['track']==None:
			continue
		thisId=track['track']['id']
		if thisId == None:
			continue
		thisName=track['track']['name']
		if verbose:
			print('Current track: ' + thisName)

		
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
			#refresh()
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
		'''
		update = refresh()
		if update == 1:
			token_info = sp_oauth.get_cached_token()
			token = token_info['access_token']
			sp = spotipy.Spotify(auth=token)
		authenticate()
		'''
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


#%% Function for downloading tracks
def downloadTracks(track):
	
	if not os.path.exists('Audio'):
		os.makedirs('Audio')
	
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



#%% Function for searching for playlists
	
def searchPlaylists(searchWord, number=50, market=None):
	# get token
	
	#token_info = sp_oauth.get_cached_token()
	#token = token_info['access_token']
	#sp=spotipy.Spotify(auth=token)
	
	global sp
	
	# searching maxes out at 50, so if number > 50, then do it multiple times
	reps = 0
	limit = number
	if number > 50:
		reps = math.floor(number/50)
		remainder = number % 50
		limit = 50
	else:
		remainder = 0
	# initiate a dataframe to hold playlists
	column_names = ['playlistID','playlistName','nTracks', 'type', 'owner', 'description', 'url']
	playlistDF = pd.DataFrame(columns = column_names)
	
	searchType = 'playlist'
	offset = 0
	for n in range(0, reps+1):
		# for last round of search, update limit to remainder
		if n == reps and number > 50:
			limit = remainder
			
		# do the search
		#refresh()
		if limit != 0:
			searchResults = sp.search(searchWord, limit=limit, offset=offset, type=searchType, market=market)
		else:
			break
		
		for thisPlaylist in searchResults['playlists']['items']:
			thisEntry = [{'playlistID':thisPlaylist['id'], 
					   'playlistName':thisPlaylist['name'], 
					   'nTracks':thisPlaylist['tracks']['total'],
					   'type':thisPlaylist['owner']['type'],
					   'owner':thisPlaylist['owner']['id'],
					   'description':thisPlaylist['description'],
					   'url':thisPlaylist['owner']['external_urls']['spotify']}]
			#print(thisEntry)
			#print('\n')
			playlistDF = playlistDF.append(thisEntry, ignore_index=True)
		# break loop if we get less results than the limit
		if len(searchResults['playlists']['items']) < limit:
			break
		# now update offset
		offset += 50

	return playlistDF

#%% Function for getting addition playlist information
	
def getPlaylistFollowers(playlistIDs):
	# this just gets the playlist followers in a separate function
	# be aware that using this function in addition to the others may put you into rate limit at the Spotify API
	
	global sp
	
	# initiate a dataframe to hold playlist info
	column_names = ['playlistID','nFoll']
	playlistDF = pd.DataFrame(columns = column_names)
	
	
	for playlistID in playlistIDs:
		thisPlaylistInfo = sp.playlist(playlistID, 'followers')
		
		thisFollowers = thisPlaylistInfo['followers']['total']
		
		if thisFollowers is None:
			thisFollowers = 0
		
		thisEntry = [{'playlistID':playlistID,
				'nFoll':thisFollowers}]
		playlistDF = playlistDF.append(thisEntry, ignore_index=True)
		
		

	return playlistDF



#%% Function for getting albums
	

def getAlbumInformation(thisAlbum, verbose=False, asDataFrame=False):
	
	global sp
	
	thisSaveName = 'Albums/' + thisAlbum + '.pkl'
	
	# now check if the file already exists
	if os.path.isfile(thisSaveName):
		return thisSaveName
	
	if verbose:
		print('Getting audio features and information from albums.')
	
	if not os.path.exists('Albums'):
		os.makedirs('Albums')
		
	
	column_names = ['AlbumID', 'AlbumName', 'TrackNumber', 'TrackName', 'TrackID', 'SampleURL', 'ReleaseYear', 'Genres', 'danceability', 'energy', 
				'loudness', 'speechiness', 'acousticness', 'instrumentalness',
				'liveness', 'valence', 'tempo', 'key', 'mode', 'duration_ms']
	albumDF = pd.DataFrame(columns = column_names)
	# Sleep a little bit to not piss of Spotify
	thisSleep = random.randint(0,10) * 0.01
	time.sleep(thisSleep)
	
	
	try:
		theseTracks = sp.album(thisAlbum)
	except:
		# handle errors with getting tracks
		theseTracks = 0
		thisDict = [{'AlbumID':'EMPTYDATAFRAME',
			   'AlbumName':'EMPTYDATAFRAME',
			   'TrackNumber':0,  
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
		albumDF = albumDF.append(thisDf, ignore_index=True)
		return 'error'
	
	thisAlbumName = theseTracks['name']
	#print(thisAlbumName)
	thisReleaseDate = theseTracks['release_date']
	thisPopularity = theseTracks['popularity']
	
	if thisPopularity == None:
			thisPopularity=-1
		
	if thisReleaseDate == None:
		thisReleaseDate = 0
	
	
	tracks = theseTracks['tracks']['items']
	while theseTracks['tracks']['next']:
		#authenticate()
		theseTracks = sp.next(theseTracks)
		tracks.extend(theseTracks['tracks']['items'])
	
	for track in tracks:
		if track==None:
			continue
		thisId=track['id']
		if thisId == None:
			continue
		thisName=track['name']
		if verbose:
			print('Current track: ' + thisName)
		
		thisTrackNumber = track['track_number']

		
		
			
		# genre is linked to artist, not to song. Therefore, need another get here.
		# first get artist.
		# will get the first artist, there might be numerous

		thisArtistId = track['artists'][0]['id']
		if thisArtistId == None:
			thisGenres = '[unknown]'
		else:
			#refresh()
			try:
				thisArtistInfo = sp.artist(thisArtistId)
				thisGenres = thisArtistInfo['genres']
			except:
				thisGenres = []
			if thisGenres == []:
				thisGenres = '[unknown]'
		
		
		thisUrl=track['preview_url']
		# Sleep a little bit to avoid rate limiting
		thisSleep = random.randint(0,10)*0.09
		time.sleep(thisSleep)
		# Get audio features for the track
		
		thisFeature=sp.audio_features(tracks=thisId)
		
		# Create a dataframe entry
		if thisFeature[0]!=None:
			thisDict = [{'AlbumID':thisAlbum,
				'AlbumName':thisAlbumName,
				'TrackName':thisName,
				'TrackNumber':thisTrackNumber,
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
			albumDF = albumDF.append(thisDf, ignore_index=True)

	
	# do a check here to see if empty 
	if albumDF.empty:
		thisDict = [{'AlbumID':'EMPTYDATAFRAME',
			   'AlbumName':'EMPTYDATAFRAME',  
			   'TrackName':'EMPTYDATAFRAME',
			   'TrackNumber':0,
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
		albumDF = albumDF.append(thisDf, ignore_index=True)
		
	# save as pickle here
	albumDF.to_pickle(thisSaveName)
	
	if asDataFrame:
		output = albumDF
	else:
		output = thisSaveName
	
	
	
	return output