import sqlite3

connection = sqlite3.connect("Quriel.db")
first = connection.cursor()


# Track queries
def addTrack(name, artist, album, genre, released, address):
    # data = first.execute("""SELECT * FROM track""")
    # print("track table data: \n", data.description)
    try:
        first.execute(
            "INSERT INTO track(name, artist, album, genre, released, address) VALUES (? , ? , ? , ? , ? , ? ) ",
            (name, artist, album, genre, released, address))
        connection.commit()
    except sqlite3.Error as error:
        print("An error occurred getting playlists... ", error)


def getTrackByPath(address):
    first.execute("SELECT * FROM track WHERE address=?", (address,))
    return first.fetchall()


def getTracks():
    first.execute("SELECT * FROM track")
    return first.fetchall()


def deleteTracksByID(ID):
    first.execute("DELETE from track WHERE rowid = ?", (ID,))
    first.execute("DELETE from playlist_track WHERE track_ID=?", (ID,))
    connection.commit()


# Library queries
def getGenre(genre):
    first.execute("SELECT * from track WHERE genre = ? ", (genre,))
    return first.fetchall()


def getAlbum(album):
    first.execute("SELECT * FROM track WHERE album  = ?", (album,))
    return first.fetchall()


def getArtist(artist):
    first.execute("SELECT * FROM track WHERE artist = ?", (artist,))
    return first.fetchall()


# Playlist queries
def addPlaylist(name, trackList):
    # data = first.execute("""SELECT * FROM playlist""")
    # print("Playlist table data: \n", data.description)
    try:
        first.execute("INSERT INTO playlist(playlist_name) VALUES (?) ", (name,))
        element = first.lastrowid
        playlist = []
        for i in range(len(trackList)):
            playlist.append((i + 1, trackList[i], element,))

        first.executemany("INSERT INTO playlist_track(track_number, track_ID, playlist_ID) "
                          "VALUES (? , ? , ? ) ", playlist)
        connection.commit()
    except sqlite3.Error as error:
        print("An error occurred adding playlist... ", error)


def getPlaylist(ID):
    first.execute("""SELECT track_id, address FROM playlist_track INNER JOIN track ON
    playlist_track.track_id=track.id WHERE playlist_id = ? ORDER BY
    playlist_track.track_number
    """, (ID,))

    return first.fetchall()


def getPlaylists():
    # data = first.execute("""SELECT * FROM playlist_track""")
    # print("Playlist_track table data: \n", data.description)
    try:
        first.execute("""
            SELECT DISTINCT playlist_track.playlist_ID, playlist.playlist_name
            FROM playlist_track
            INNER JOIN playlist
            ON playlist.id = playlist_track.playlist_ID
        """)
        return first.fetchall()

    except sqlite3.Error as error:
        print("An error occurred getting playlists... ", error)


def deletePlaylist(name):
    try:
        first.execute("DELETE FROM playlist WHERE ID = ?", (name,))
        first.execute("DELETE FROM playlist_track WHERE playlist_ID = ? ", (name,))
        connection.commit()
    except sqlite3.Error as error:
        print("An error occurred deleting playlist... ", error)
