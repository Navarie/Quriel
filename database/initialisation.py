import sqlite3

connection = sqlite3.connect("Quriel.db")
cursor = connection.cursor()

cursor.execute(
    """CREATE TABLE track(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, 
        artist TEXT, 
        album TEXT, 
        genre TEXT,
        released INTEGER, 
        address TEXT) 
    """)

cursor.execute(
    """CREATE TABLE playlist_track(
        track_number INTEGER, 
        track_ID INTEGER, 
        playlist_ID INTEGER)
    """)

cursor.execute(
    """CREATE TABLE playlist( 
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT)
    """)
