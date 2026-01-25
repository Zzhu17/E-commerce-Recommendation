import pandas as pd


def temporal_split(df: pd.DataFrame, train_end: str, val_end: str):
    df = df.copy()
    df["event_ts"] = pd.to_datetime(df["event_ts"])
    train_end_ts = pd.to_datetime(train_end)
    val_end_ts = pd.to_datetime(val_end)

    train_df = df[df["event_ts"] <= train_end_ts].copy()
    test_df = df[(df["event_ts"] > train_end_ts) & (df["event_ts"] <= val_end_ts)].copy()
    return train_df, test_df
