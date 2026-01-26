import pandas as pd

from src.data.split import temporal_split


def test_temporal_split_basic():
    df = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 2],
            "product_id": [10, 11, 20, 21],
            "event_ts": pd.to_datetime([
                "2015-05-01",
                "2015-06-10",
                "2015-05-20",
                "2015-06-12",
            ]),
        }
    )
    train, test = temporal_split(df, "2015-06-01", "2015-06-15")
    assert len(train) == 2
    assert len(test) == 2
