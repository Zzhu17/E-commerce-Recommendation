# Data Diagnostics

Run the diagnostics script to populate this report and generate plots:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rocket"
python experiments/data_diagnostics.py
```

This will generate:
- `artifacts/diagnostics/user_history_hist.png`
- `artifacts/diagnostics/item_popularity_longtail.png`

And populate summary stats (sparsity, long-tail share, interaction counts).
