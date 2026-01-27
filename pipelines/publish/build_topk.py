import argparse
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--user-emb", required=True)
    parser.add_argument("--item-emb", required=True)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    user_emb = np.load(args.user_emb)
    item_emb = np.load(args.item_emb)

    k = args.k
    rows = []
    for u in range(user_emb.shape[0]):
        scores = user_emb[u] @ item_emb.T
        topk = np.argpartition(scores, -k)[-k:]
        topk = topk[np.argsort(scores[topk])[::-1]]
        for rank, i in enumerate(topk, 1):
            rows.append({
                "user_id": u,
                "rank": rank,
                "item_id": int(i),
                "score": float(scores[i]),
            })

    df = pd.DataFrame(rows)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(out)


if __name__ == "__main__":
    main()
