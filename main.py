import datetime
import json
import pandas as pd
import requests
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sqlite3

DATABASE_NAME = "my_played_tracks"
DATABASE_FILE = DATABASE_NAME + ".sqlite"
DATABASE_LOCATION = "sqlite:///" + DATABASE_FILE
USER_ID = "Wes"
TOKEN = "BQDAQeUsElI8Fx94dinYcBTXl0GH84oJ7OXlLfx1P-ut2QOb84s0BPk5HQka12yIefOSPNUKknNV6Y0JvdyDyVZS1bQ5D2zVat7P_upte8ahalwVlhkItZnIGmptF9jU8fDqXkvF8VavMSh83hVmU2segnkMNIiV9BaG2eJt"

def check_valid_data(df: pd.DataFrame) -> bool:

    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution.")
        return False
    
    # Primary key check
    if pd.Series(df["played_at"]).is_unique:
        pass
    else:
        raise Exception("Primary Key is violated")
    
    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null value is found")

    # Check if all timestamps are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
  
    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
            raise Exception("At least one of the returned song does not come from within the last 24 hours")
    


if __name__ == "__main__":
    
    headers = {
        "Accept": "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=TOKEN)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_ut = int(yesterday.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_ut), headers=headers)
    data = r.json()

    print(data)

    data_song = []
    data_artist = []
    data_played_at = []
    data_timestamp = []

    for song in data["items"]:
        data_artist.append(song["track"]["artists"][0]["name"])
        data_song.append(song["track"]["name"])
        data_played_at.append(song["played_at"])
        data_timestamp.append(song["played_at"][:10])

    dict_song = {
        "song": data_song,
        "artist": data_artist,
        "played_at": data_played_at,
        "timestamp": data_timestamp
    }

    df_song = pd.DataFrame(dict_song, columns= ["song", "artist", "played_at", "timestamp"])

    # Validate
    if check_valid_data(df_song):
        print("Data valid, proceeding to loading stage")

    # Load
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song VARCHAR(200),
        artist VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_query)
    print("Database successfully opened.")

    try:
        df_song.to_sql(DATABASE_NAME, engine, index=False, if_exists="append")
    except:
        print("Data already exists in the database")

    conn.close()
    print("Database successfuly closed.")
