import os
import math
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import psycopg2

from src.data.split import temporal_split
from src.data.graph import build_mappings, build_train_edges, build_user_pos
from src.evaluation.bootstrap import bootstrap_ci
from src.evaluation.metrics import coverage_at_k, diversity_at_k, hit_at_k, ndcg_at_k
from src.recommenders.popularity import fit_popularity, recommend_popularity
from src.recommenders.time_decay_popularity import fit_time_decay_popularity
from src.recommenders.user_cf import build_matrix, recommend_user_cf
from src.recommenders.lightgcn import LightGCNConfig, train_lightgcn, recommend_lightgcn
from src.recommenders.als import ALSConfig, build_user_item_matrix, fit_als, recommend_als


@dataclass
class EvalConfig:
    train_end: str
    val_end: str
    sample_mod: int
    candidate_size: int
    k: int
    seed: int
    bootstrap_enabled: bool
    bootstrap_resamples: int
    models: List[dict]


def load_interactions(sample_mod: int, val_end: str) -> pd.DataFrame:
    db_url = os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket")
    sql = f"""
        SELECT user_id, product_id, event_ts
        FROM analytics.fact_events
        WHERE event_type IN ('view', 'addtocart', 'transaction')
          AND user_id % {int(sample_mod)} = 0
          AND event_ts <= '{val_end}'
        ORDER BY user_id, event_ts
    """
    with psycopg2.connect(db_url) as conn:
        return pd.read_sql_query(sql, conn)


def load_categories(item_ids: List[int]) -> Dict[int, int]:
    if not item_ids:
        return {}
    db_url = os.getenv("DATABASE_URL", "postgresql://rocket:Zzp990812@localhost:5434/rocket")
    items_csv = ",".join(str(int(item_id)) for item_id in item_ids)
    sql = f"""
        SELECT product_id, category_id
        FROM analytics.dim_product
        WHERE product_id IN ({items_csv})
    """
    with psycopg2.connect(db_url) as conn:
        df = pd.read_sql_query(sql, conn)
    return dict(zip(df["product_id"], df["category_id"]))


def build_y_true(test_df: pd.DataFrame) -> Dict[int, set]:
    return test_df.groupby("user_id")["product_id"].apply(set).to_dict()


def assign_segments(train_df: pd.DataFrame) -> Dict[int, str]:
    counts = train_df.groupby("user_id")["product_id"].count()
    segments = {}
    for user_id, cnt in counts.items():
        if cnt <= 2:
            segments[user_id] = "cold"
        elif cnt <= 10:
            segments[user_id] = "light"
        else:
            segments[user_id] = "heavy"
    return segments


def filter_candidates(train_df: pd.DataFrame, test_df: pd.DataFrame, candidate_size: int):
    top_items = train_df["product_id"].value_counts().head(candidate_size).index.tolist()
    train_df = train_df[train_df["product_id"].isin(top_items)].copy()
    test_df = test_df[test_df["product_id"].isin(top_items)].copy()
    return train_df, test_df, top_items


def evaluate_config(config: EvalConfig) -> Tuple[List[dict], List[dict], dict]:
    t0 = time.time()
    df = load_interactions(config.sample_mod, config.val_end)
    train_df, test_df = temporal_split(df, config.train_end, config.val_end)
    train_df = train_df[["user_id", "product_id", "event_ts"]].dropna()
    test_df = test_df[["user_id", "product_id"]].dropna()

    train_df, test_df, candidate_items = filter_candidates(
        train_df, test_df, config.candidate_size
    )

    y_true = build_y_true(test_df)
    users = sorted(set(train_df["user_id"]).intersection(y_true.keys()))
    train_df = train_df[train_df["user_id"].isin(users)].copy()
    y_true = {u: y_true[u] for u in users}

    item_to_category = load_categories(candidate_items)
    user_segments = assign_segments(train_df)

    n_interactions = len(train_df)
    n_users = len(users)
    n_items = len(candidate_items)

    metrics = []
    segment_metrics = []

    cached_recs = {}
    graph_mapping = None
    edges = None
    user_pos_idx = None
    user_items = None

    def ensure_graph():
        nonlocal graph_mapping, edges, user_pos_idx, user_items
        if graph_mapping is None:
            graph_mapping = build_mappings(users, candidate_items)
            edges = build_train_edges(train_df, graph_mapping)
            user_pos_idx = build_user_pos(edges)
            user_items = build_user_item_matrix(edges, n_users, n_items)
    for model_cfg in config.models:
        model_name = model_cfg["name"]
        start_train = time.time()

        if model_name == "popularity":
            ranked_items = fit_popularity(train_df, candidate_items)
            train_seconds = time.time() - start_train
            start_infer = time.time()
            recs = recommend_popularity(users, ranked_items, config.k)
            infer_seconds = time.time() - start_infer
        elif model_name == "time_decay_popularity":
            ranked_items = fit_time_decay_popularity(
                train_df,
                candidate_items,
                train_end=config.train_end,
                half_life_days=model_cfg.get("params", {}).get("half_life_days", 14),
            )
            train_seconds = time.time() - start_train
            start_infer = time.time()
            recs = recommend_popularity(users, ranked_items, config.k)
            infer_seconds = time.time() - start_infer
        elif model_name == "user_cf":
            matrix, user_index, item_index = build_matrix(train_df, users, candidate_items)
            train_seconds = time.time() - start_train
            start_infer = time.time()
            recs = recommend_user_cf(
                matrix,
                users,
                user_index,
                item_index,
                config.k,
                top_neighbors=model_cfg.get("params", {}).get("top_neighbors", 50),
            )
            infer_seconds = time.time() - start_infer
        elif model_name == "als":
            ensure_graph()
            cfg = ALSConfig(
                factors=model_cfg.get("params", {}).get("factors", 64),
                regularization=model_cfg.get("params", {}).get("reg", 0.01),
                iterations=model_cfg.get("params", {}).get("iterations", 30),
                alpha=model_cfg.get("params", {}).get("alpha", 1.0),
            )
            als_model = fit_als(user_items, cfg)
            train_seconds = time.time() - start_train
            start_infer = time.time()
            recs_idx = recommend_als(als_model, user_items, list(range(n_users)), config.k)
            idx2item = graph_mapping.idx2item
            recs = {users[u_idx]: [idx2item[i_idx] for i_idx in items] for u_idx, items in recs_idx.items()}
            infer_seconds = time.time() - start_infer
        elif model_name == "lightgcn":
            ensure_graph()
            cfg = LightGCNConfig(
                embedding_dim=model_cfg.get("params", {}).get("dim", 64),
                num_layers=model_cfg.get("params", {}).get("num_layers", 3),
                lr=model_cfg.get("params", {}).get("lr", 1e-3),
                batch_size=model_cfg.get("params", {}).get("batch_size", 2048),
                num_neg=model_cfg.get("params", {}).get("num_neg", 1),
                epochs=model_cfg.get("params", {}).get("epochs", 50),
                reg=model_cfg.get("params", {}).get("reg", 1e-4),
                seed=config.seed,
                device=model_cfg.get("params", {}).get("device"),
            )
            user_emb, item_emb, _ = train_lightgcn(edges, user_pos_idx, n_users, n_items, cfg)
            train_seconds = time.time() - start_train
            start_infer = time.time()
            recs_idx = recommend_lightgcn(
                user_emb,
                item_emb,
                user_pos_idx,
                config.k,
                batch_size=model_cfg.get("params", {}).get("score_batch", 512),
            )
            idx2item = graph_mapping.idx2item
            recs = {users[u_idx]: [idx2item[i_idx] for i_idx in items] for u_idx, items in recs_idx.items()}
            infer_seconds = time.time() - start_infer
        elif model_name == "hybrid_rule":
            rule = model_cfg.get("params", {})
            recs = {}
            start_infer = time.time()
            for user_id in users:
                segment = user_segments.get(user_id, "cold")
                model_for_user = rule.get(segment, "popularity")
                source = cached_recs.get(model_for_user)
                if source is None:
                    raise ValueError(f"Hybrid rule missing cached model: {model_for_user}")
                recs[user_id] = source.get(user_id, [])
            train_seconds = time.time() - start_train
            infer_seconds = time.time() - start_infer
        else:
            raise ValueError(f"Unknown model: {model_name}")

        cached_recs[model_name] = recs

        hit = hit_at_k(y_true, recs, config.k)
        ndcg = ndcg_at_k(y_true, recs, config.k)
        coverage = coverage_at_k(recs, candidate_items, config.k)
        diversity = diversity_at_k(recs, item_to_category, config.k)

        hit_ci_low = hit_ci_high = None
        if config.bootstrap_enabled:
            user_hits = []
            user_ndcg = []
            for user_id, true_items in y_true.items():
                pred_items = recs.get(user_id, [])[:config.k]
                user_hits.append(int(bool(true_items.intersection(pred_items))))
                if pred_items:
                    dcg = 0.0
                    for rank, item_id in enumerate(pred_items):
                        if item_id in true_items:
                            dcg += 1.0 / math.log2(rank + 2)
                    ideal_hits = min(len(true_items), config.k)
                    idcg = sum(1.0 / math.log2(rank + 2) for rank in range(ideal_hits)) if ideal_hits else 0.0
                    user_ndcg.append(dcg / idcg if idcg else 0.0)
            hit_ci_low, hit_ci_high = bootstrap_ci(
                user_hits,
                n_resamples=config.bootstrap_resamples,
                seed=config.seed,
            )

        metrics.append(
            {
                "model": model_name,
                "hit_at_k": round(hit, 4),
                "ndcg_at_k": round(ndcg, 4),
                "coverage_at_k": round(coverage, 4),
                "diversity_at_k": round(diversity, 4),
                "hit_ci_low": None if hit_ci_low is None else round(hit_ci_low, 4),
                "hit_ci_high": None if hit_ci_high is None else round(hit_ci_high, 4),
                "train_seconds": round(train_seconds, 4),
                "infer_seconds": round(infer_seconds, 4),
                "n_users": n_users,
                "n_items": n_items,
                "n_interactions": n_interactions,
            }
        )

        for segment in ("cold", "light", "heavy"):
            seg_users = [u for u in users if user_segments.get(u) == segment]
            seg_true = {u: y_true[u] for u in seg_users}
            seg_recs = {u: recs.get(u, []) for u in seg_users}
            if not seg_users:
                continue
            segment_metrics.append(
                {
                    "model": model_name,
                    "segment": segment,
                    "k": config.k,
                    "candidate_size": config.candidate_size,
                    "sample_mod": config.sample_mod,
                    "seed": config.seed,
                    "hit_at_k": round(hit_at_k(seg_true, seg_recs, config.k), 4),
                    "ndcg_at_k": round(ndcg_at_k(seg_true, seg_recs, config.k), 4),
                    "coverage_at_k": round(coverage_at_k(seg_recs, candidate_items, config.k), 4),
                    "diversity_at_k": round(diversity_at_k(seg_recs, item_to_category, config.k), 4),
                    "n_users": len(seg_users),
                }
            )

    timing = {
        "total_seconds": round(time.time() - t0, 4),
    }
    return metrics, segment_metrics, timing
