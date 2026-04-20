import pandas as pd

from src.data.split import temporal_split
from src.evaluation.metrics import hit_at_k, ndcg_at_k


def test_data_split_to_metric_flow():
    events = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 2, 3, 3],
            "product_id": [101, 102, 201, 202, 301, 302],
            "event_ts": pd.to_datetime(
                [
                    "2015-05-01",
                    "2015-05-20",
                    "2015-05-15",
                    "2015-06-11",
                    "2015-05-22",
                    "2015-06-10",
                ]
            ),
        }
    )

    train, test = temporal_split(events, "2015-06-01", "2015-06-15")

    assert train.shape[0] == 4
    assert test.shape[0] == 2

    truth = {2: {202}, 3: {302}}
    recs = {2: [202, 201], 3: [300, 302]}

    assert hit_at_k(truth, recs, k=2) == 1.0
    assert ndcg_at_k(truth, recs, k=2) > 0.8
