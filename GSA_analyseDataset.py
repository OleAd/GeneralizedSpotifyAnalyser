# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 09:14:35 2021

@author: olehe

This example script shows how to do some basic analysis and visualization

"""
#%% Do imports

# for handling data
import pandas as pd

# plot-related libraries
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import ptitprince as pt
from wordcloud import WordCloud
from collections import Counter

# for easier access to file system
import os

# for stats
import pingouin as pg



#%% Read in dataset

dataset = pd.read_csv('Data/metal_dataset_uniqueTracks.csv', encoding='UTF-8', na_values='', index_col=0)


# make a folder for plots
if not os.path.exists('Plots'):
	os.makedirs('Plots')

#%% First, let's take a look at genres


# get the genres, and split them into individual entries
# Select first the Finnish genres
finnishGenres = list(dataset[dataset['category'] == 'Finnish']['Genres'])


# strip and replace bits in the Genre strings
finnishGenres_long = []
for thisTrack in finnishGenres:
	thisTrackGenres = thisTrack.replace('\'', '').replace('[', '').replace(']', '').replace(', ', ',').split(',')
	finnishGenres_long.extend(thisTrackGenres)


# Select the Norwegian genres
norwegianGenres = list(dataset[dataset['category'] == 'Norwegian']['Genres'])

norwegianGenres_long = []
for thisTrack in norwegianGenres:
	thisTrackGenres = thisTrack.replace('\'', '').replace('[', '').replace(']', '').replace(', ', ',').split(',')
	norwegianGenres_long.extend(thisTrackGenres)
	

# Make a wordcloud plot for Norwegian metal genres
	
# Count the occurence of each genre	
norwegianGenres_count = Counter(norwegianGenres_long)
# Make the Wordcloud
norwegianWordcloud = WordCloud(stopwords='unknown', 
							   height=700, 
							   width=1400, 
							   min_font_size=4,
							   colormap=matplotlib.cm.inferno,
							   background_color='white').generate_from_frequencies(norwegianGenres_count)
# Save the Wordcloud
norwegianWordcloud.to_file('Plots/norwegianGenres.png')


# Make a wordcloud plot for Finnish metal genres
finnishGenres_count = Counter(finnishGenres_long)
finnishWordcloud = WordCloud(stopwords='unknown', 
							   height=700, 
							   width=1400, 
							   min_font_size=4,
							   colormap=matplotlib.cm.inferno,
							   background_color='white').generate_from_frequencies(finnishGenres_count)
finnishWordcloud.to_file('Plots/finnishGenres.png')



#%% Now lets look at release years

# Get first four letters of ReleaseYear column as integers
finnishYear = dataset[dataset['category'] == 'Finnish']['ReleaseYear'].str[0:4].astype(int)
# filter out any marked as '0' (unknown release date)
finnishYear = finnishYear[finnishYear > 0]

finnishYearPlot = sns.displot(finnishYear, kind='kde', clip=(1940,2021), bw_adjust=.5)
finnishYearPlot.set(xlim=(1938,2021), ylim=(0,0.07))
finnishYearPlot.savefig('Plots/FinnishYear.png', bbox_inches='tight')


# Get first four letters of ReleaseYear column as integers
norwegianYear = dataset[dataset['category'] == 'Norwegian']['ReleaseYear'].str[0:4].astype(int)
# filter out any marked as '0' (unknown release date)
norwegianYear = norwegianYear[norwegianYear > 0]

norwegianYearPlot = sns.displot(norwegianYear, kind='kde', clip=(1940,2021), bw_adjust=.5)
norwegianYearPlot.set(xlim=(1938,2021), ylim=(0,0.07))
norwegianYearPlot.savefig('Plots/NorwegianYear.png', bbox_inches='tight')


#%% Do a little bit of statistics on the audio features

# First let's subset our dataset to contain only category, and the audio features

audiofeatures = dataset[['category',
						 'danceability',
						 'energy',
						 'loudness',
						 'speechiness',
						 'acousticness',
						 'instrumentalness',
						 'liveness',
						 'valence',
						 'tempo',
						 'key',
						 'mode']]

	
# The simplest example is doing t-tests between each feature, and correcting
# for multiple comparisons. Viable alternatives are manova, 
# multiple logistic regression, or linear discriminant analysis, amongst others
	

# we'll separate the data into two dataframes
norwegianValues = audiofeatures[audiofeatures['category']=='Norwegian']
finnishValues = audiofeatures[audiofeatures['category']=='Finnish']

# list of the comparisons we'll do:
features = ['danceability','energy','loudness','speechiness','acousticness',
			 'instrumentalness','liveness','valence','tempo']

# this will hold the statistics
statHolder = pd.DataFrame()

# do the comparisons in a loop
for thisFeature in features:
	# unpaired two-sample T-test using Pingouin
	output = pg.ttest(finnishValues[thisFeature], norwegianValues[thisFeature],
				      paired=False,
					  tail='two-sided',
					  correction='auto')
	output['feature'] = thisFeature
	statHolder = statHolder.append(output, ignore_index=True)
	
# then lets do a simple Bonferroni correction
bonferroniCorrected = pg.multicomp(list(statHolder['p-val']), alpha=.01, method='bonf')

# extract the corrected p-values
statHolder['p-corr'] = bonferroniCorrected[1]
# extract a logical array if test is significant
statHolder['significant'] = bonferroniCorrected[0]


# write the statistics to file
statHolder.to_csv('Data/metalComparison.csv', encoding='UTF-8')


#%% Now lets look at the audio features

# We'll make raincloud plots for most of the audio features by looping through them
features = ['danceability','energy','loudness','speechiness','acousticness',
			 'instrumentalness','liveness','valence','tempo']

# make the plots in a loop
for thisFeature in features:
	# Make a name for the figure
	saveName = 'Plots/MetalComparison-' + thisFeature + '.png'
	# draw the plot
	f, ax = plt.subplots(figsize=(7,5), dpi=300)
	pt.RainCloud(x='category', y=thisFeature, data=audiofeatures, palette='Set2', bw=.2, 
				  width_viol=.6, move=.2, ax=ax, orient='h', point_size=.35,
				  box_showfliers = False)
	# Let's try to draw statistics in the plot as well
	# get stats for this feature
	thisStat = statHolder[statHolder['feature']==thisFeature].reset_index()
	# check if significant
	isSignificant = thisStat['significant']
	signifStar = ''
	if isSignificant[0]:
		# you can use this to add a significance star somewhere
		signifStar = '* '
	# get p-value
	pVal = thisStat['p-corr']
	# need to format the pVal a bit, since they are quite low numbers, and P=0.0 doesn't look good
	# if pVal is below 0.0001, then print as p < 0.001
	if float(pVal.round(3))<0.001:
		pVal = '< 0.001'
	else:
		pVal = '= ' + str(float(pVal.round(3)))
	
	
	# get Cohen's d-value
	dVal = thisStat['cohen-d']
	# make a string with the statistics
	statText = signifStar + 'P ' + pVal + ', Cohen\'s D = ' + str(float(dVal.round(3)))
	# add title
	plt.suptitle(thisFeature.capitalize())
	# add statistics
	plt.title(statText)
	plt.xlabel('Value')
	plt.ylabel('')
	# save the figure
	plt.savefig(saveName, bbox_inches='tight')



	

















