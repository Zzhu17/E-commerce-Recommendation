# 🛍️ E-commerce User Behavior + Conversion Recommendation System

A complete data science project that analyzes user behavior, predicts conversion probability, and recommends top products using interpretable models and Tableau dashboards.

---

## 📌 Project Structure

```
ecommerce_recommender_template/
├── data/                     # Raw interaction data (interactions.csv)
├── notebooks/                # Jupyter Notebooks (EDA, Modeling, Recommendation)
│   └── output/recommendations/ → Recommendation PNG charts
├── output/                   # Model outputs (predictions, SHAP plots, etc.)
│   └── shap/                 → SHAP bar plot & summary plot
├── models/                   # Model training, prediction & explanation scripts
│   ├── conversion_model.py   → Train model to predict conversion
│   ├── conversion_model.pkl  → Trained model artifact
│   ├── shap_analysis.py      → SHAP explainability visualization
│   ├── conversion_recommender.py → Recommend items for likely converters
├── src/                      # Data loading, preprocessing, app integration
│   ├── app/app.py            → FastAPI app (optional deployment)
│   └── data/                 → Preprocessing and feature engineering
├── utils/                    # Output export & visualization utilities
├── tableau/                  # (Optional) Tableau workbook and assets
├── README.md                 # Project documentation
├── requirements.txt          # Dependency list
└── veer/                     # Your virtual environment (should not be committed)
```

---

## 🔍 Features

- 📊 **EDA & User Clustering**: Analyze RFM features, k-means segmentation.
- 🎯 **Conversion Prediction**: RandomForestClassifier + SHAP interpretability.
- 🤖 **Recommendation Logic**: Recommend items for high-conversion users.
- 📈 **Visualization**: Static PNGs + Tableau Dashboard support.
- 💡 **Explainability**: Global feature importance with SHAP (bar + summary plots).

---

## 🚀 Quick Start

1. **Install dependencies** (activate your environment first):

```bash
pip install -r requirements.txt
```

2. **Run Notebooks** (in order):
   - `EDA.ipynb`
   - `Modeling.ipynb`
   - `Recommendation.ipynb`

3. **SHAP Explainability** (optional):

```bash
python models/shap_analysis.py
```

4. **Tableau Dashboard**:
   - Import `summary_plot.png` and `importance_bar_plot.png` from `output/shap/`
   - Import `top_items.png` and `top_users.png` from `notebooks/output/recommendations/`

---

## 📁 Outputs

- `output/users_with_prediction.csv`: All users with conversion probability.
- `output/recommendations.csv`: Top-N item recommendations for high converters.
- `output/shap/*.png`: SHAP explanation charts.
- `notebooks/output/recommendations/*.png`: Recommendation result charts.

---

## ⚙️ Tech Stack

- Python, Pandas, Scikit-learn
- SHAP for interpretability
- Tableau Public for dashboard
- Jupyter Notebooks for workflow