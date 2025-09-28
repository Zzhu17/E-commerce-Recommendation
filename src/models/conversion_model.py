from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import joblib
from typing import Optional

def train_conversion_model(df, target_col: str, feature_cols: list, save_path: Optional[str] = None):
    X = df[feature_cols]
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [5, 10, None]
    }
    grid = GridSearchCV(model, param_grid, cv=3, scoring='roc_auc')
    grid.fit(X_train, y_train)

    best = grid.best_estimator_
    print("Best params:", grid.best_params_)
    print("Train AUC:", grid.score(X_train, y_train))
    print("Test AUC:", grid.score(X_test, y_test))

    if save_path:
        joblib.dump(best, save_path)

    return best
