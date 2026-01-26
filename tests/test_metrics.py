import math

from src.evaluation.metrics import coverage_at_k, diversity_at_k, hit_at_k, ndcg_at_k


def test_hit_at_k_basic():
    y_true = {1: {10, 20}, 2: {30}}
    y_pred = {1: [5, 10], 2: [1, 2]}
    assert hit_at_k(y_true, y_pred, k=2) == 0.5


def test_ndcg_at_k_basic():
    y_true = {1: {10}, 2: {30}}
    y_pred = {1: [10, 20], 2: [40, 30]}
    expected = (1.0 + 1.0 / math.log2(3)) / 2
    assert abs(ndcg_at_k(y_true, y_pred, k=2) - expected) < 1e-6


def test_coverage_at_k_basic():
    recs = {1: [10, 20], 2: [20, 30]}
    items = [10, 20, 30, 40]
    assert coverage_at_k(recs, items, k=2) == 0.75


def test_diversity_at_k_basic():
    recs = {1: [10, 20], 2: [30, 40]}
    item_to_cat = {10: 1, 20: 1, 30: 2, 40: 3}
    assert diversity_at_k(recs, item_to_cat, k=2) == 0.75
