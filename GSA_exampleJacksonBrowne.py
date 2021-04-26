# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:06:48 2021

@author: olehe

This scripts shows a simple example of checking the discography of Jackson Browne
"""

#%% Do imports

# for handling data
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.decomposition import PCA

# plot-related libraries
import seaborn as sns
import matplotlib.pyplot as plt

# for easier access to file system
import os

# for breakpoints
import ruptures as rpt

# import GSA
import GSA

# multiprocessing for improved speeed
from joblib import Parallel, delayed

# tqdm for progressbar
from tqdm import tqdm

# make a folder for plots
if not os.path.exists('Plots'):
	os.makedirs('Plots')



#%% Authenticate
GSA.authenticate()

#%% Read in dataset
dataset = pd.read_csv('Data/JacksonBrowne.csv', encoding='UTF-8', na_values='', index_col=None)

# This CSV contains a column "AlbumURI" which we'll use to get the album IDs
allAlbums = dataset.AlbumURI.tolist()

# Extract just ID, by taking index 14:36.
allAlbumsID = [thisAlbum[14:36] for thisAlbum in allAlbums]

# Add back into the dataset
dataset['AlbumID'] = allAlbumsID


#%% Get tracks from album
IDlist_tqdm = tqdm(allAlbumsID, desc='Getting audio features') 
results = Parallel(n_jobs=6, require='sharedmem')(delayed(GSA.getAlbumInformation)(thisAlbum) for thisAlbum in IDlist_tqdm)
# set n_jobs to as many threads you want your to use on your cpu.

#%% Add the supplementary information to the dataframe

# First collect all the albums, as not all might have been successfully downloaded
output=[]
for thisList in results:
	if thisList == 'error':
		print('Found an album not downloaded.')
	else:
		thisFrame = pd.read_pickle(thisList)
		output.append(thisFrame)
	
# Flatten
output = pd.concat(output)

# Remove any where TrackName is EMPTYDATAFRAME
empties = output[output['TrackName'] == 'EMPTYDATAFRAME']
output.drop(empties.index, inplace=True)

# Merge with original dataset to get supplementary information	
merged_output = dataset.merge(output, on ='AlbumID', how='left')

# Uncomment to save dataset
# merged_output.to_csv('Data/Jackson_Browne_dataset.csv', encoding='UTF-8')


#%% Getting album level data.

# We're interested in album level data
# Let's calculate mean and std values of the audio features for each album

# NOTE: this could most likely be streamlined. Open a PR on GitHub if you can make this section better
albumLevelMean = merged_output[['AlbumName',
							   'AlbumOrder',
							   'danceability',
							   'energy',
							   'loudness',
							   'speechiness',
							   'acousticness',
							   'instrumentalness',
							   'liveness',
							   'valence',
							   'tempo']].groupby(by=['AlbumName']).mean().sort_values(by=['AlbumOrder']).reset_index()

albumLevelStd = merged_output[['AlbumName',
							   'AlbumOrder',
							   'danceability',
							   'energy',
							   'loudness',
							   'speechiness',
							   'acousticness',
							   'instrumentalness',
							   'liveness',
							   'valence',
							   'tempo']].groupby(by=['AlbumName']).std().sort_values(by=['AlbumOrder']).reset_index().add_suffix('_std')


albumLevelData = pd.concat([albumLevelMean, albumLevelStd], axis=1)
albumLevelData.drop(columns=['AlbumName_std', 'AlbumOrder_std'], inplace=True)


#%% Analyse data

# Extract only audio features
audioFeatures = albumLevelData.drop(columns=['AlbumName', 'AlbumOrder'])

# Extract album titles to shorten some of the titles
albumNames = albumLevelData['AlbumName']
# shorten some of the names
albumNames[0] = 'Jackson Browne'
albumNames[4] = 'Running on Empty'


# Normalize data using a MinMax scaler
scaler = preprocessing.MinMaxScaler()
scaledData = scaler.fit_transform(audioFeatures.values)
scaledAudioFeatures = pd.DataFrame(scaledData, columns=audioFeatures.columns)

# Calculate breakpoints
model = rpt.Dynp(model='rbf', min_size=1).fit(np.array(scaledAudioFeatures))
breakpoints = model.predict(n_bkps=2)


# Inspect breakpoints
rpt.display(scaledAudioFeatures['acousticness'], breakpoints)
plt.show()


#%% Make plot

sns.set_style('darkgrid') # set a visual style

# initiate plot
plt.figure(figsize=(12,4))
# draw lineplot
timelinePlot = sns.lineplot(data=scaledAudioFeatures[['acousticness', 'valence']])
# set the x labels, and rotate them a bit for readability
timelinePlot.set_xticks(range(0,14))
timelinePlot.set_xticklabels(labels=albumNames, rotation=30, ha='right')
timelinePlot.set_xlabel('')
timelinePlot.set_xlim([0,13])
# add a title
timelinePlot.set_title('Change point analysis of Browne\'s discography', fontsize=16)
# add vertical lines from the breakpoint calculation
timelinePlot.vlines(breakpoints[0:2], ymin=timelinePlot.get_ylim()[0], ymax=timelinePlot.get_ylim()[1], linestyles='dashed')
# also add background colouring of the breakpoints
bColour = [0, 5, 10, 13]
colours=['b', 'r', 'b']
for n in range(0, len(bColour)-1):
	timelinePlot.axvspan(bColour[n], bColour[n+1], facecolor=colours[n], alpha=.2)

tickColours = ['r', 'b']
# finally, color the x labels according to my likes
for count, tick in enumerate(timelinePlot.get_xticklabels()):
	tick.set_color(tickColours[dataset['Like'][count]])



#%% Just a quick look at PCA

# Try this is you want to check the PCA components as a way of plotting 
pca = PCA(n_components=2)
pcaFeatures = pca.fit_transform(scaledAudioFeatures)

# turn into dataframe
pcaFeaturesDF = pd.DataFrame(data = pcaFeatures,
							 columns = ['PCA_1', 'PCA_2'])
pcaFeaturesDF.set_index(albumNames, inplace=True)








