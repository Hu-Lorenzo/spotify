from flask import Flask, redirect, request, url_for, render_template,session
import spotipy
from spotipy.oauth2 import SpotifyOAuth


#le tue credenziali le trovi nella dashboard di prima
SPOTIFY_CLIENT_ID = "ef05fc98d68d46298e93a2da2b717946"
SPOTIFY_CLIENT_SECRET = "15e5ce3c623e41b09b85c37d125d2021"
SPOTIFY_REDIRECT_URI = "https://5000-hulorenzo-spotify-oa13perg86f.ws-eu117.gitpod.io/callback" #dopo il login andiamo qui

app = Flask(__name__)
app.secret_key = 'chiave_per_session' #ci serve per identificare la sessione

#config SpotifyOAuth per l'autenticazione e redirect uri
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-private",
    show_dialog=True
)

@app.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url() #login di spotify
    return redirect(auth_url)
@app.route('/callback')
def callback():
    code = request.args.get('code') #recupero codice di autorizzazione
    token_info = sp_oauth.get_access_token(code) #uso il code per un codice di accesso
    session['token_info'] = token_info #salvo il token nella mia sessione x riutilizzarlo
    return redirect(url_for('home'))
@app.route('/home', methods=['GET', 'POST'])
def home():
    token_info = session.get('token_info', None)  
    if not token_info:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])  
    user_info = sp.current_user()
    playlists = sp.current_user_playlists()['items']  

    tracks = []  

    if playlists:  
        playlist_id = request.args.get('playlist_id', playlists[0]['id'])  
        
        playlist_tracks = sp.playlist_items(playlist_id)

        tracks = [{
            'name': track['track']['name'],
            'artist': track['track']['artists'][0]['name'],
            'album': track['track']['album']['name'],
            'image': track['track']['album']['images'][0]['url'] if track['track']['album']['images'] else None
        } for track in playlist_tracks['items']]

    return render_template('home.html', user_info=user_info, playlists=playlists, tracks=tracks)


@app.route('/logout')
def logout():
    session.clear() #cancelliamo l'access token salvato in session
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)