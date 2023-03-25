# --------------------------------------------------- #

from __future__ import annotations
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from random import randint, random, choice, sample
from math import floor, ceil
from datetime import datetime
import json
import argparse
from time import sleep

# --------------------------------------------------- #

parser = argparse.ArgumentParser(
                    prog='SpotifyScripting',
                    description='plays a playlist')
parser.add_argument('filename', nargs='?', default="example")
args = parser.parse_args()
filename = args.filename

def create_spotify_client():

    with open("config.txt") as f:
        spotify_client_id, spotify_client_secret, = (i[-32:] for i in f.read().splitlines())

    spotify_client_scopes   = "user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative user-read-playback-position user-top-read user-library-read"
    spotify_client_callback = "https://google.com/"

    auth_manager = SpotifyOAuth(client_id=spotify_client_id,
                            client_secret=spotify_client_secret,
                            redirect_uri=spotify_client_callback,
                            scope=spotify_client_scopes)

    return spotipy.Spotify(auth_manager=auth_manager)

sp = create_spotify_client()

# --------------------------------------------------- #

# alternate random functions rand and choose
rand = random
def choose(*args):
    if len(args) == 1:
        try: return args[0] if isinstance(args[0], str) else choice(args[0])
        except: return args[0]
    return choice(args)

# --------------------------------------------------- #

# saves playlist URIs by name
with open("playlists.txt") as f:
    cached_user_playlists = {x: y for x,y in (line.split(" | ") for line in f.read().splitlines())}

with open("tracks.json") as f:
    cached_tracks = json.loads(f.read())

# --------------------------------------------------- #

# generally, these functions work by searching with the spotify API, then returning data found by this API as actual data

# gets a playlist using the cached URI or the URI from search if not found, then retrieving the items from the API
def get_playlist(spotify_client, playlist_query):
    if playlist_query.lower() in cached_user_playlists: playlist_id = cached_user_playlists[playlist_query.lower()]
    else: playlist_id = spotify_client.search(q=playlist_query, type='playlist', limit=1)['playlists']['items'][0]['uri']
    return playlist([track(item["track"]["id"]) for item in spotify_client.playlist(playlist_id)['tracks']['items']])


# gets an artist / album by search and returns the API data
def get_artist(spotify_client, artist_query):
    artist_id = spotify_client.search(q=artist_query, type='artist', limit=1)['artists']['items'][0]['uri']
    return spotify_client.artist(artist_id)

def get_album(spotify_client, album_query):
    album_id = spotify_client.search(q=album_query, type='album', limit=1)['albums']['items'][0]['uri']
    return spotify_client.album(album_id)

# gets a track by cached data or by search if unavailable
def get_track(spotify_client, track_query):
    if isinstance(track_query, dict): return track_query
    if track_query in cached_tracks: return cached_tracks[track_query]
    if (sanitised := "spotify:track:" + track_query) in cached_tracks: return cached_tracks[sanitised]
    elif "spotify:track" in track_query: track_id = track_query
    else:
        try: track_id = spotify_client.search(q=track_query, type='track', limit=1)['tracks']['items'][0]['uri']
        except: return spotify_client.track(track_query, market="GB")
    return spotify_client.track(track_id, market="GB")

# --------------------------------------------------- #

# a custom error raiser which has syntax I like (and shows the spotify script code rather than the python code)
def raise_error(line_number: int, error_type: BaseException, error_message: str):
    raise error_type(f"\n\n\nTraceback: exception on line {line_number + 1}\n>>> {lines[line_number]}\n{str(error_type)[8:-2]}: {error_message}\n")

# all the keywords that can start off a line of code
approved_instructions = [
    "if", "else", "elseif", "fi",
    "jumpto", "coda", "while", "repeat", 
    "play", "var", "pass", "quit"
]

# --------------------------------------------------- #

# a custom range class that can match against integers on one or both ends
class span:
    def __init__(self, lower: int | None, upper: int | None) -> None:
        self.lower = lower
        self.upper = upper

    # represents either a one-ended or two-ended span (or a dummy span) as text
    def __repr__(self) -> str:
        if self.lower is None and self.upper is None:
            return f"span(any)"
        elif self.lower is None:
            return f"span(<={self.upper})"
        elif self.upper is None:
            return f"span(>={self.lower})"
        else:
            return f"span({self.lower}-{self.upper})"

    # matches a number object if it is in the range
    def match(self, item):
        try: item = int(item)
        except: AttributeError: raise_error(line_number, AttributeError, f"Cannot filter non-number item {item} by range {self.__repr__()}.")

        if self.lower is None and self.upper is None:
            return True
        elif self.lower is None:
            return item <= self.upper
        elif self.upper is None:
            return item >= self.lower
        else:
            return self.lower <= item <= self.upper


# filters an individual item of a collection by specified attribute
def filter_matches(item, i, x):
    try: to_match = item.__getattribute__(i)
    except AttributeError: raise_error(line_number, AttributeError, f"Cannot filter by nonexistent attribute {i}.")
    if isinstance(x, span):
        return x.match(to_match)
    return x == to_match
    

# a custom list-based class - the items attribute is a list, with other methods built on top
class playlist:
    def __init__(self, items) -> None:
        if isinstance(items, str):
            self.items = get_playlist(sp, items)
        else: self.items = items

    # getting a single item gives you that item, getting a slice gives you a playlist object
    def __getitem__(self, index):
        if isinstance(index, float) or isinstance(index, int):
            return self.items[int(index)]
        elif isinstance(index, slice):
            return playlist(self.items[index])
    
    # filtering the items in the playlist by arbitrary attributes using filter_matches
    def filter(self, **kwargs) -> playlist:
        return playlist([item for item in self.items
                           if all((filter_matches(item, i, x) for i,x in kwargs.items()))])
    
    def __len__(self) -> int:
        return len(self.items)
    
    def __repr__(self) -> str:
        return f"<Playlist({len(self)} songs)>"


# --------------------------------------------------- #


# represents an artist, with some data on them
class artist:
    def __init__(self, query_or_json: dict | str) -> None:

        # json object provided directly or found from json
        self.json = query_or_json if isinstance(query_or_json, dict) else get_artist(sp, query_or_json)
        
        # data taken from json
        self.followers = self.json["followers"]["total"]
        self.id = self.json["uri"]
        self.name = self.json["name"]
        self.genres = self.json["genres"]

    # all albums from an artist as a list of album objects
    @property
    def albums(self):
        items = sp.artist_albums(self.id, ["album", "single"], "GB", limit=50)["items"]
        return playlist([album(item) for item in items])
    
    def __repr__(self) -> str:
        return f"<Artist({self.name})>"
    
    
# an album class with a list of tracks and some metadata
class album:
    def __init__(self, query_or_json: dict | str) -> None:

        # json object provided directly or found from jsom
        self.json = query_or_json if isinstance(query_or_json, dict) else get_album(sp, query_or_json)

        self.artist = self.json["artists"][0]["name"]
        self.year = int(self.json["release_date"][:4])
        self.length = int(self.json["total_tracks"])
        self.name = self.json["name"]
        self.id = self.json["uri"]

    # returns the list of tracks in the album as a playlist object
    @property
    def tracks(self):
        items = sp.album_tracks(self.id, self.length, market="GB")["items"]
        return playlist([track(item["uri"]) for item in items])
    
    def __len__(self) -> int:
        return self.length
    
    def __repr__(self) -> str:
        return f"<Album({self.name})>"
    
    # essentially converts into a playlist object to use the filter method
    def filter(self, **kwargs):
        return self.tracks.filter(**kwargs)


# track data can be provided directly, retrieved from cache, or searched for (get_track function handles this logic)
class track:
    def __init__(self, query_or_json: dict | str) -> None:

        self.json = get_track(sp, query_or_json)

        # all data available about the track
        self.artist = self.json["album"]["artists"][0]["name"]
        self.year = int(self.json["album"]["release_date"][:4])
        self.duration = self.json["duration_ms"] // 1000
        self.name = self.json["name"]
        self.id = self.json["uri"]
        self.position = int(self.json["track_number"])
        self.popularity = int(self.json["popularity"])

        self.json = {
            "name": self.name,
            "uri": self.id,
            "track_number": self.position,
            "popularity": self.popularity,
            "duration_ms": self.duration * 1000,
            "album": {"artists": [{"name": self.artist}],
                      "release_date": str(self.year)},

        }

        if self.id not in cached_tracks:
            cached_tracks[self.id] = self.json

    def __len__(self): return 1

    def __repr__(self) -> str:
        return f"<Track({self.name})>"


# --------------------------------------------------- #

def play_song(song_uri):
    try: sp.add_to_queue(song_uri)
    except:
        sp.start_playback()
        sleep(0.5)
        sp.add_to_queue(song_uri)

# --------------------------------------------------- #

# load file to be interpreted line-by-line
with open(f"Playlists/{filename}.txt") as f:
    lines = f.read().replace(" filtered by ", ".filter").splitlines()

# skipping_lines_condition is None | int | str for no jumping, jump to line, jump to coda
skipping_lines_condition: None | int | str = None
# skipping_ifs_condition is 0 for no skipping, 1 for skipping to next branch, 2 for skipping to fi when done with branch, 3 for just going to fi
skipping_ifs_condition: int = 0

# --------------------------------------------------- #

# interpret file line by line
for line_number, raw_line in enumerate(lines):
    
    # process the line, and skip if it's a comment or a blank line
    line = raw_line.strip()
    if line == "" or line.startswith("#"): continue

    # verbose instructions, finds line keyword to match as the first word
    keyword = line.split()[0]

    # jumpto <line number> or jumpto <sentinel> are matched and the line is skipped if so
    if isinstance(skipping_lines_condition, int) and line_number + 1 == skipping_lines_condition:
        skipping_lines_condition = None
    elif isinstance(skipping_lines_condition, str) and line == f"coda {skipping_lines_condition}":
        skipping_lines_condition = None
    if skipping_lines_condition is not None:
        continue

    if keyword not in approved_instructions:
        raise_error(line_number, SyntaxError, f"\"{keyword}\" is not a valid line descriptor.")

    # if we're going to the next condition, or the end of a branch block
    if skipping_ifs_condition == 1 and keyword not in ("elseif", "else", "fi"): continue
    if skipping_ifs_condition == 2 and keyword in ("elseif", "else", "fi"): skipping_ifs_condition = 3
    if skipping_ifs_condition == 3 and keyword != "fi": continue
    if keyword == "fi": skipping_ifs_condition == 0

    match keyword:

        # once we hit a fi, the if block is done (nested if statements are not supported)
        case "fi":
            skipping_ifs_condition = 0

        # // TODO
        case "while": raise_error(line_number, NotImplementedError, "while loops are not yet implemented!")
        case "repeat": raise_error(line_number, NotImplementedError, "while loops are not yet implemented!")


        # jumpto line sets an integer, and jumpto <trigger> sets a string
        case "jumpto":
            skipping_lines_condition = line[6:].strip()
            try: skipping_lines_condition = int(skipping_lines_condition)
            except: pass

        # declaring or setting a variable
        case "var":

            # strips to after the "var"
            line = line[3:]

            # line should take the form "var x = (expression)"
            try: variable_name, expression = line.split("=", 1)
            except: raise_error(line_number, SyntaxError, "Variable is declared but not given a value.")

            # filters variable name to alphabetical + underscores
            variable_name = variable_name.strip()
            if not all((c.isalpha() or c == "_" for c in variable_name)):
                raise_error(line_number, SyntaxError, "Invalid variable name - only alphabetic characters and underscores are allowed.")
            
            # turns syntax into its pythonic version
            modified_expression = expression.replace("!", " not ").replace("|", " or ").replace("&", " and ").replace("^", "**")
            
            # evaluates the result
            try: result = float(eval(expression))
            except NameError as e: raise_error(line_number, NameError, e)
            except ValueError: raise_error(line_number, ValueError, e)

            # sets the variable
            exec(f"{variable_name} = {result}")
            
        # branch logic keywords: else always evaluates to True (run the branch if we're not skipping)
        case kw if kw in ("if", "else", "elseif"):
            if kw == "else": modified_expression = "True"
            else: modified_expression = line.split(" ", 1)[1].replace("!", " not ").replace("|", " or ").replace("&", " and ").replace("^", "**")
            
            # run the branch until the next check if condition is true, otherwise skip to next condition statement
            skipping_ifs_condition = 2 if eval(modified_expression) else 1

        # stop interpreting the file
        case "quit": break

        # play one or more tracks
        case "play":

            # split into how many to play and where to play from and evaluate both
            quantity, source = line[5:].split(" from ")
            source = eval(source)
            quantity = len(source) if quantity == "all" else min(len(source), int(eval(quantity)))
            
            # plays differently based on source type
            if isinstance(source, album):
                for song in (sample(source.tracks.items, quantity)):
                    play_song(song.id)

            if isinstance(source, playlist):
                for song in sample(range(0, len(source)), quantity):
                    play_song(source[song].id)

            if isinstance(source, track):
                play_song(source.id)

        case _: pass


# saves the song cache
with open("tracks.json", "w+") as f:
    json.dump(cached_tracks, f)
