# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 10:23:03 2021


Basic example for GSA
This script gets audio features for one playlist,
then downloads preview MP3s.

@author: olehe
"""


# First import GSA and pandas
import GSA
import pandas as pd

# Then authenticate, so you can access the Spotify API through Spotipy
# Make sure you have filled in spotifyConstants.py with your own information
GSA.authenticate()

# Now get information on one playlist. 
# You need to give the function the Spotify ID of the playlist.
# See GSA_example for more details.
# Here's an example playlist ID: 37i9dQZF1DX3hgbB9nrEB1
myPlaylist = GSA.getInformation('37i9dQZF1DX3hgbB9nrEB1')

# myPlaylist now contains the location of a .pkl-file where the information is stored.
# We save the information to a .pkl-file for easier processing of multiple playlists

# Read the .pkl-file to get a dataframe
myPlaylistInformation = pd.read_pickle(myPlaylist)


# If you want to download preview MP3s, you can use the GSA.downloadTracks function
# This function takes as input a list with the following information:
# ['SampleURL', 'TrackName', 'TrackID', 'playlistID']
# You can read this information from the myPlaylistInformation dataframe:
toDownload = myPlaylistInformation[['SampleURL', 'TrackName', 'TrackID', 'playlistID']].values.tolist()

# Create an array to keep track of which were successfully downloaded
downloaded = []
# Now download preview MP3s, in a loop:
for track in toDownload:
	print('Downloading track: ' + track[1]) # this prints the current track name
	success = GSA.downloadTracks(track)
	downloaded.append(success)


# Downloaded now contains a list with trackIDs followed by a 1 for succesfully downloaded previews



