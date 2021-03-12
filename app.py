import streamlit as st 
import pickle
import scraper
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os

#defining spotify oauth parameters
scope = 'playlist-modify-public'
client_id = os.environ['client_id']
client_secret = os.environ['client_secret']

#initializing spotify oauth
oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://localhost:8080/',
    scope=scope
    )

#defining global variables
genres = list(pickle.load(open('genres.pkl', 'rb'))).sort()
years = list(range(1990,2022))

#defining app functions
#spotify only allows 20 albums per request so bigger playlists need to be broken up
def break_up_albums(album_ids, sp):
    trax = []
    size = len(album_ids)
    if size <= 20:
        for album in list(sp.albums(album_ids)['albums']):
            trax.extend([x['id'] for x in album['tracks']['items']])
        return trax
    else:
        while size > 20:
            case = album_ids[size-20:size]
            for album in list(sp.albums(case)['albums']):
                trax.extend([x['id'] for x in album['tracks']['items']])
            size = size - 20
            time.sleep(1)
        case = album_ids[:size]
        for album in list(sp.albums(case)['albums']):
                trax.extend([x['id'] for x in album['tracks']['items']])
        return trax

#search function to find tracks on spotify and create list of track IDs to add to the playlist
def search_spotify(releases, sp):
    album_ids = []
    for release in releases:
        results = sp.search(q= f"{release['artist']} {release['title']}", type='album', limit=1)
        if any(results['albums']['items']):
            album_ids.append(results['albums']['items'][0]['id'])
        else:
            print(f"Couldn't find {release['artist']}, {release['title']} :(")
            continue
        my_bar.progress(releases.index(release) + 1)
        time.sleep(1)
    st.balloons()
    return break_up_albums(album_ids, sp)

#function checks length of tracklist and adds songs according the the API limit (100 tracks per request)
def confirm_and_add(results, username, playlist_id, sp):
    size = len(results)
    if size <= 100:
        return sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=results)
    else:
        while size > 100:
            case = results[size-100:size]
            sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=case)
            size = size - 100
            time.sleep(3)
        case = results[:size]
        return sp.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=case)

#initialize progress bar
my_bar = st.progress(0)

def main():
    st.title('Nodata.tv Spotify Playlist Maker')
    st.header('By Xristos Katsaros')
    st.subheader('This app utilizes web scraping to find releases covered by Nodata.tv and places them in a Spotify playlist')

    st.header('Connect to Spotify')
    
    #look for cached token
    token_info = oauth.get_cached_token()

    #request a new token if none found
    if not token_info:
        auth_url = oauth.get_authorize_url()
        st.write(auth_url)
        response = st.text_input('Click the above link, then copy & paste the url in the new tab here, then press enter: ')
        if response == "":
            time.sleep(5)
        code = oauth.parse_response_code(response)
        token_info = oauth.get_access_token(code)
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)
    else:
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)
    
    st.header('Select playlist preferences')
    st.text('Number of pages to scrape on the Nodata blog')
    pages = st.selectbox('Pages', list(range(1,1800)))
    user_genre1 = st.selectbox('Genre 1', genres)
    user_genre2 = st.selectbox('Genre 2', genres)
    user_genres = [user_genre1, user_genre2]
    username = st.text_input('Spotify username')
    playlist_name = st.text_input('Name of new or existing playlist')
    year = str(st.selectbox('Year', years))

    if st.button('Make playlist'):
        #get the names of of all the user's playlists
        playlists = [x['name'].lower() for x in sp.current_user_playlists()['items']]

        st.write('User Playlists:')
        for playlist in playlists:
            st.text(playlist)

        #determine playlist ID
        if playlist_name not in playlists:
            sp.user_playlist_create(user=username, name=playlist_name) #create a new playlist
            playlist_id = sp.current_user_playlists()['items'][0]['id'] #grab new playlist ID
        elif playlist_name in playlists:
            playlist_id = sp.current_user_playlists()['items'][playlists.index(playlist_name)]['id'] #find ID of existing playlist

        #the 2 main functions for scraping & searching spotify
        scrape_results = scraper.scrape(int(pages), user_genres, year) #scrapes nodata.tv
        spotify_results = search_spotify(scrape_results, sp) #inserts scraped results into search function

        confirm_and_add(spotify_results, username, playlist_id, sp)


if __name__ == '__main__':
    main()