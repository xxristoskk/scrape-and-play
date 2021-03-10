import streamlit as st 
import pickle
import scraper
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

scope = 'playlist-modify-public'


genres = pickle.load(open('genres.pkl', 'rb'))
years = list(range(1990,2022))

oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://localhost/',
    scope=scope
    )

def main():
    st.title('Nodata.tv Spotify Playlist Maker')
    
    pages = st.selectbox('Pages', list(range(1,300)))
    user_genres = st.selectbox('Genre 1', list(genres))
    playlist_name = st.text_input('Name of new or existing playlist')
    # year = st.selectbox('Year', years)

    if st.button('Make playlist'):
        #look for cached token
        token_info = oauth.get_cached_token()

        #request a new token if none found
        if not token_info:
            auth_url = oauth.get_authorize_url()
            st.write(auth_url)
            response = st.text_input('Click the above link, then paste the redirect url here and hit enter: ')
            if response == "":
                time.sleep(5)
            code = oauth.parse_response_code(response)
            token_info = oauth.get_access_token(code)
            token = token_info['access_token']
            sp = spotipy.Spotify(auth=token)
        else:
            token = token_info['access_token']
            sp = spotipy.Spotify(auth=token)

        def break_up_albums(album_ids):
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
        def search_spotify(releases):
            album_ids = []
            for release in releases:
                results = sp.search(q= f"{release['artist']} {release['title']}", type='album', limit=1)
                if any(results['albums']['items']):
                    album_ids.append(results['albums']['items'][0]['id'])
                else:
                    print(f"Couldn't find {release['artist']}, {release['title']} :(")
                    continue
                time.sleep(1)
            return break_up_albums(album_ids)
        playlists = [x['name'].lower() for x in sp.current_user_playlists()['items']]

        #determine playlist ID
        if playlist_name not in playlists:
            sp.user_playlist_create(user='xristosk', name=playlist_name) #create a new playlist
            playlist_id = sp.current_user_playlists()['items'][0]['id'] #grab new playlist ID
        elif playlist_name in playlists:
            playlist_id = sp.current_user_playlists()['items'][playlists.index(playlist_name)]['id'] #find ID of existing playlist

        scrape_results = scraper.scrape(int(pages), user_genres) #scrapes nodata.tv
        spotify_results = search_spotify(scrape_results) #inserts scraped results into search function

        #function checks length of tracklist and adds songs according the the API limit (100 tracks per request)
        def confirm_and_add(results):
            size = len(results)
            if size <= 100:
                return sp.user_playlist_add_tracks(user='xristosk', playlist_id=playlist_id, tracks=results)
            else:
                while size > 100:
                    case = results[size-100:size]
                    sp.user_playlist_add_tracks(user='xristosk', playlist_id=playlist_id, tracks=case)
                    size = size - 100
                    time.sleep(3)
                case = results[:size]
                return sp.user_playlist_add_tracks(user='xristosk', playlist_id=playlist_id, tracks=case)

        confirm_and_add(spotify_results)


if __name__ == '__main__':
    main()