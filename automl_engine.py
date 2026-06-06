import warnings
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import (GradientBoostingClassifier, GradientBoostingRegressor,
                              RandomForestClassifier, RandomForestRegressor)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error,
                             mean_squared_error, precision_score, r2_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings('ignore')

class AutoMLEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    def detect_problem_type(self, target_col: str) -> str:
        if target_col not in self.df.columns:
            return "unknown"
        unique_vals = self.df[target_col].nunique()
        if self.df[target_col].dtype in ['object', 'category', 'bool']:
            if unique_vals == 2:
                return "binary_classification"
            return "multiclass_classification"
        else:
            if unique_vals <= 10 and unique_vals / len(self.df) < 0.05:
                return "multiclass_classification"
            return "regression"

    def suggest_targets(self) -> List[str]:
        suggestions = []
        for col in self.df.columns:
            unique = self.df[col].nunique()
            if self.df[col].dtype in ['object', 'category', 'bool']:
                if 2 <= unique <= 50:
                    suggestions.append(col)
            else:
                if unique <= 20 and unique / len(self.df) < 0.1:
                    suggestions.append(col)
                elif unique > 20:
                    suggestions.append(col)
        return suggestions[:5] if suggestions else list(self.df.columns)[:5]

    def prepare_data(self, target_col: str, test_size: float = 0.2):
        df_clean = self.df.copy()

        # Handle target
        y = df_clean[target_col].copy()
        if y.isnull().all():
            return None, None, None, None

        # Drop rows where target is null
        valid_mask = y.notnull()
        df_clean = df_clean[valid_mask].copy()
        y = y[valid_mask].copy()

        if len(df_clean) < 5:
            return None, None, None, None

        # Encode target if categorical
        if self.df[target_col].dtype in ['object', 'category', 'bool']:
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.values

        # Drop target from features
        X = df_clean.drop(columns=[target_col]).copy()

        # Encode categoricals
        for col in X.select_dtypes(include=['object', 'category', 'bool']).columns:
            X[col] = X[col].astype(str)
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])

        # Select only numeric features
        X = X.select_dtypes(include=[np.number])

        if X.shape[1] == 0:
            return None, None, None, None

        # Fill missing values
        X = X.fillna(X.median())

        # Determine if stratification is possible
        stratify = None
        unique_y = np.unique(y)
        if len(unique_y) < 10 and len(unique_y) > 1:
            # Check if every class has at least 2 samples (needed for stratify)
            class_counts = pd.Series(y).value_counts()
            if (class_counts >= 2).all():
                stratify = y

        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=stratify
            )
        except ValueError:
            # Fallback: non-stratified split
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42
                )
            except ValueError:
                return None, None, None, None

        return X_train, X_test, y_train, y_test

    def run_classification(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        models = {
            "Logistic Regression": LogisticRegression(max_iter=2000, random_state=42),
            "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=10),
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        results = []
        best_model = None
        best_score = -1

        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                acc = accuracy_score(y_test, preds)
                prec = precision_score(y_test, preds, average='weighted', zero_division=0)
                rec = recall_score(y_test, preds, average='weighted', zero_division=0)
                f1 = f1_score(y_test, preds, average='weighted', zero_division=0)
                result = {
                    "model": name,
                    "accuracy": round(float(acc), 4),
                    "precision": round(float(prec), 4),
                    "recall": round(float(rec), 4),
                    "f1_score": round(float(f1), 4),
                    "status": "success"
                }
                if acc > best_score:
                    best_score = acc
                    best_model = (name, model)
                results.append(result)
            except Exception as e:
                results.append({"model": name, "error": str(e), "status": "failed"})

        # Feature importance from best tree model
        feature_importance = {}
        if best_model and hasattr(best_model[1], 'feature_importances_'):
            feature_importance = dict(zip(X_train.columns, best_model[1].feature_importances_))
            feature_importance = {k: round(float(v), 4) for k, v in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)}

        return {
            "problem_type": "classification",
            "leaderboard": sorted(results, key=lambda x: x.get("accuracy", 0), reverse=True),
            "best_model": best_model[0] if best_model else None,
            "feature_importance": feature_importance,
            "classes": int(len(np.unique(y_train)))
        }

    def run_regression(self, X_train, X_test, y_train, y_test) -> Dict[str, Any]:
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        results = []
        best_model = None
        best_score = -999999

        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                mae = mean_absolute_error(y_test, preds)
                rmse = np.sqrt(mean_squared_error(y_test, preds))
                r2 = r2_score(y_test, preds)
                result = {
                    "model": name,
                    "mae": round(float(mae), 4),
                    "rmse": round(float(rmse), 4),
                    "r2_score": round(float(r2), 4),
                    "status": "success"
                }
                if r2 > best_score:
                    best_score = r2
                    best_model = (name, model)
                results.append(result)
            except Exception as e:
                results.append({"model": name, "error": str(e), "status": "failed"})

        feature_importance = {}
        if best_model and hasattr(best_model[1], 'feature_importances_'):
            feature_importance = dict(zip(X_train.columns, best_model[1].feature_importances_))
            feature_importance = {k: round(float(v), 4) for k, v in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)}

        return {
            "problem_type": "regression",
            "leaderboard": sorted(results, key=lambda x: x.get("r2_score", -999), reverse=True),
            "best_model": best_model[0] if best_model else None,
            "feature_importance": feature_importance
        }

    def run(self, target_col: str) -> Dict[str, Any]:
        problem = self.detect_problem_type(target_col)

        if problem == "unknown":
            return {"error": "Could not detect problem type for the selected target column"}

        X_train, X_test, y_train, y_test = self.prepare_data(target_col)

        if X_train is None:
            return {"error": "Insufficient data for modeling. Need at least 5 rows with valid target and numeric features."}

        if problem in ["binary_classification", "multiclass_classification"]:
            return self.run_classification(X_train, X_test, y_train, y_test)
        else:
            return self.run_regression(X_train, X_test, y_train, y_test)
