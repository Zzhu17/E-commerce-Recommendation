# 🛒 E-commerce User Behavior & Marketing Recommendation System

This project analyzes e-commerce user interaction data to predict conversion probability, cluster users, and provide personalized marketing recommendations.  
It supports both **Data Analyst** and **Data Scientist** career paths, with optional integration of **SQL + Tableau** and **SHAP-based ML explainability**.

---

## 🔍 Project Overview

### 🔹 Data Sources:
- `data/interactions.csv`: Raw user interaction records
- `data/converted_features.csv`: Processed features for model training (conversion prediction)

---

## 📊 Features

| Component                     | Description                                                  |
|------------------------------|--------------------------------------------------------------|
| 🔧 `preprocess.py`            | Feature engineering (adds device, country, visit count, session duration) |
| 🧠 `conversion_model.py`      | Trains RandomForestClassifier to predict conversion          |
| 🧠 `conversion_recommender.py`| Rule-based recommender system for high-probability users     |
| 📉 `shap_analysis.py`         | SHAP feature explainability with bar + summary plots         |
| 📈 `export_outputs.py`        | Export CSV and PNG outputs                                   |
| 📦 `Recommendation.ipynb`     | End-to-end pipeline: predict → recommend → visualize         |
| 📊 `Tableau Dashboard`        | Combines SQL charts + SHAP plots into a single dashboard     |
| 🗃️ `MySQL Integration`        | Analyze conversion by device, country, behavior segments     |

---

## 🧮 SQL + MySQL Support (Data Analyst Path)

We use MySQL to perform behavioral segmentation and conversion rate analysis.

### ✅ Tables Created:
- `converted_features`: Enhanced with `device`, `country`, `num_visits`, `session_duration`

### ✅ SQL Script:
- `sql/analysis_queries.sql`: Analyzes conversion rate by:
  - Country
  - Device
  - Visit frequency
  - Session duration

### ✅ Python Integration:
Use `mysql-connector-python` and `SQLAlchemy` to fetch query results and plot with matplotlib/seaborn.

---

## 🧠 SHAP + Explainability (Data Scientist Path)

- Uses SHAP TreeExplainer to interpret model predictions
- Exports:
  - `summary_plot.png`
  - `importance_bar_plot.png`
- Integrated into Tableau Dashboard

---

## 📁 Project Structure (Simplified)

```
├── data/
│   ├── interactions.csv
│   └── converted_features.csv
├── notebooks/
│   ├── output/recommendations
│   ├── EDA.ipynb
│   ├── Modeling.ipynb
│   └── Recommendation.ipynb
├── src/
│   ├── models/
│   ├── utils/
│   └── app/
├── output/
│   ├── shap/
│   └── recommendations/
├── sql/
│   └── analysis_queries.sql
├── tableau/
│   └── (Tableau dashboards & assets)
├── README.md
└── requirements.txt
```
---

## 🚀 How to Run

### 📌 1. Setup Environment
```bash
pip install -r requirements.txt
---
### 📌 2. Preprocess Data
python preprocess.py

### 📌 3. Load Data to MySQL
python load_data_to_mysql.py

### 📌 4. Run SQL Analysis
mysql -u root -p ecommerce_db < sql/analysis_queries.sql

### 📌 5. Train Model
jupyter notebook notebooks/Modeling.ipynb

### 📌 6. SHAP Analysis
python src/models/shap_analysis.py

###📌 7. Tableau Dashboard

## 🚀 Quick Start

**Install dependencies** (activate your environment first):

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