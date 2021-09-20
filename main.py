import csv
import json
import os
import requests
import youtube_dl
import collections
import pandas as pd
from refresh import Refresh
from urllib.parse import urlencode
from secrets import spotify_playlist_id, yt_playlist_id

class Spotify(object):

    def __init__(self):
        self.spotify_token = ""
        self.playlist_id = spotify_playlist_id
        self.yt_playlist_id = yt_playlist_id
        self.search_track_endpoint = 'https://api.spotify.com/v1/search'
        self.songs_info  = collections.defaultdict(list)
        self.uri_check = []
        
    def authorization(self):
        refreshCaller = Refresh()

        self.spotify_token = refreshCaller.refresh()
        youtube = refreshCaller.YTcredentials()
        self.YTlikedmusic(youtube)

    def YTlikedmusic(self, youtube):

        pl_request = youtube.playlistItems().list(
                part = 'snippet,contentDetails', playlistId = yt_playlist_id
                )
        
        pl_response = pl_request.execute()

        if not os.path.exists("ext.csv"):
            with open('ext.csv', 'a+', newline = '') as f:
                writer = csv.writer(f)
                for item in pl_response["items"]:
                    writer.writerow([item['contentDetails']["videoId"]])

                    youtube_url = "https://www.youtube.com/watch?v={}".format(
                    item['contentDetails']["videoId"])
                    video = youtube_dl.YoutubeDL({}).extract_info(
                    youtube_url, download=False)

                    if video["track"] is not None and video["artist"] is not None:
                        self.songs_info["track"].append(video["track"])
                        self.songs_info["artist"].append(video["artist"])
            f.close()
        else:
            df = pd.read_csv('ext.csv', header=None, names = ["uri"])
            with open('ext.csv', 'a+', newline = '') as f:
                writer = csv.writer(f)
                for item in pl_response["items"]:
                    if df['uri'].str.contains(item['contentDetails']["videoId"]).any():
                        continue
                    else:

                        writer.writerow([item['contentDetails']["videoId"]])

                        youtube_url = "https://www.youtube.com/watch?v={}".format(
                        item['contentDetails']["videoId"])
                        video = youtube_dl.YoutubeDL({}).extract_info(
                        youtube_url, download=False)
                    
                        if video["track"] is not None and video["artist"] is not None:
                            self.songs_info["track"].append(video["track"])
                            self.songs_info["artist"].append(video["artist"])    
                f.close()
            
        self.find_songs()

    def find_songs(self):
        
        self.check_if_in_spotify_playlist()
        for i in range(len(self.songs_info['track'])):
            search = {'track': '{}'.format(self.songs_info['track'][i]), 'artist': '{}'.format(self.songs_info['artist'][i])}
            
            query = ' '.join([f'{k}:{v}' for k,v in search.items()])

            data = urlencode({'q': query, 'type': 'track'})
            lookup_url = f'{self.search_track_endpoint}?{data}'

            response = requests.get(lookup_url, headers={
                        'Authorization': f'Bearer {self.spotify_token}'})
            json_response = response.json()
            liked_music = [i for i in json_response['tracks']['items']]
            
            if liked_music[0]['uri'] not in self.uri_check:
                self.songs_info["uri"].append(liked_music[0]['uri'])
        
        self.add_songs_to_spotify_playlist()

    def check_if_in_spotify_playlist(self):
        
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(spotify_playlist_id)
        
        response = requests.get(query, headers={
                        'Authorization': f'Bearer {self.spotify_token}'})
        json_response = response.json()

        for items in json_response['items']:
            self.uri_check.append(items['track']['uri'])
            
    def add_songs_to_spotify_playlist(self):

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(spotify_playlist_id)
        
        request_body = json.dumps({"uris": self.songs_info['uri']})

        requests.post(query, data = request_body,  
                            headers = {"Content-Type": "application/json",
                            "Authorization": "Bearer {}".format(self.spotify_token)})    

def main():  
    obj = Spotify()
    obj.authorization()

if __name__ == '__main__':
    main()