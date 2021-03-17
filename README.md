# GeneralizedSpotifyAnalyser
 This should contain scripts that allows for easily analysing Spotify playlists.
 
 A user guide and preprint will follow.
 
 A "get up and running" tutorial can be found here: https://oleheggli.medium.com/easily-analyse-audio-features-from-spotify-playlists-part-1-3b004cd406b3
 
 If you end up using this for research, please cite: Heggli, Ole A., Jan Stupacher, and Peter Vuust. 2021. “Diurnal Fluctuations in Musical Preference.” PsyArXiv. March 16. doi:10.31234/osf.io/6e4yw.
 
 
# Environment
 Made in Spyder 4.0.1
 
 Running in my GeneralizedSpotifyAnalyser environment
 
 Working with:
 
 Python 3.7.6
 
 spotipy 2.17.1
 
 pandas 1.0.3
 
 joblib 0.14.1
 
 tqdm 4.47.0
 
 requests 2.25.1
 
 Tested on:
 
 Windows 10 Pro 20H2
 
# Usage
 Should take a CSV with at minimum one column called 'playlistURI'
 
 This column should contain the URI of the playlist to be analysed.
 
 Any other columns are treated as supplementary information and will be retained.
 
 NOTE: make sure that any other columns are treated correctly in pandas.
 
 Use spotifyConstants_template to fill in your API keys, then rename to spotifyConstants.py
 
