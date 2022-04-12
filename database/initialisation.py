import sqlite3

connection = sqlite3.connect("Quriel.db")
cursor = connection.cursor()

cursor.execute("""DROP TABLE IF EXISTS track;""")
cursor.execute("""DROP TABLE IF EXISTS playlist_track;""")
cursor.execute("""DROP TABLE IF EXISTS playlist;""")
cursor.execute(
    """CREATE TABLE IF NOT EXISTS track(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, 
        artist TEXT, 
        album TEXT, 
        genre TEXT,
        released INTEGER, 
        address TEXT);""")

cursor.execute(
    """CREATE TABLE IF NOT EXISTS playlist( 
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT);""")

cursor.execute(
    """CREATE TABLE IF NOT EXISTS playlist_track(
        track_number INTEGER, 
        track_ID INTEGER, 
        playlist_ID INTEGER);""")
