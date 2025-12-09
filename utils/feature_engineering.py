def build_features(df):
    X = df[[
        "day_of_year",
        "hour",
        "lat",
        "lon",
        "humidity",
        "wind_speed",
        "visibility"
    ]]
    return X
