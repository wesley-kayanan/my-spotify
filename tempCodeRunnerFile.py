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

    check_valid_data(df_song)

    print(df_song)