import numpy as np


def bootstrap_ci(values, n_resamples=300, alpha=0.05, seed=42):
    if not values:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    values = np.array(values)
    means = []
    n = len(values)
    for _ in range(n_resamples):
        sample = rng.choice(values, size=n, replace=True)
        means.append(sample.mean())
    means = np.array(means)
    lower = np.quantile(means, alpha / 2)
    upper = np.quantile(means, 1 - alpha / 2)
    return float(lower), float(upper)
