import warnings
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

class DataAnalyzer:
    def __init__(self, df: pd.DataFrame, name: str = "Dataset"):
        self.df = df.copy()
        self.name = name
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    def get_profile(self) -> Dict[str, Any]:
        profile = {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "numeric_summary": {},
            "categorical_summary": {},
            "missing": {},
            "missing_pct": {},
            "duplicates": int(self.df.duplicated().sum()),
            "memory_usage_mb": round(self.df.memory_usage(deep=True).sum() / 1024**2, 2),
            "unique_values": {}
        }
        for col in self.df.columns:
            profile["missing"][col] = int(self.df[col].isnull().sum())
            profile["missing_pct"][col] = round(self.df[col].isnull().sum() / len(self.df) * 100, 2) if len(self.df) > 0 else 0
            profile["unique_values"][col] = int(self.df[col].nunique())
        if self.numeric_cols:
            profile["numeric_summary"] = self.df[self.numeric_cols].describe().to_dict()
        for col in self.categorical_cols:
            mode_val = self.df[col].mode()
            profile["categorical_summary"][col] = {
                "top": str(mode_val.iloc[0]) if not mode_val.empty else None,
                "freq": int(self.df[col].value_counts().iloc[0]) if not self.df[col].value_counts().empty else 0,
                "categories": int(self.df[col].nunique())
            }
        return profile

    def data_quality_score(self) -> Dict[str, Any]:
        total_cells = self.df.shape[0] * self.df.shape[1]
        missing_cells = self.df.isnull().sum().sum()
        duplicate_rows = self.df.duplicated().sum()
        completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 100
        uniqueness = (1 - duplicate_rows / len(self.df)) * 100 if len(self.df) > 0 else 100
        outlier_score = 100
        if self.numeric_cols and len(self.df) > 0:
            outlier_counts = 0
            for col in self.numeric_cols:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                if IQR > 0:
                    outliers = self.df[(self.df[col] < Q1 - 1.5*IQR) | (self.df[col] > Q3 + 1.5*IQR)]
                    outlier_counts += len(outliers)
            outlier_score = max(0, 100 - (outlier_counts / len(self.df)) * 10) if len(self.df) > 0 else 100
        overall = (completeness * 0.4 + uniqueness * 0.3 + outlier_score * 0.3)
        return {
            "overall": round(overall, 1),
            "completeness": round(completeness, 1),
            "uniqueness": round(uniqueness, 1),
            "outlier_score": round(outlier_score, 1),
            "missing_cells": int(missing_cells),
            "duplicate_rows": int(duplicate_rows),
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns)
        }

    def detect_outliers(self, col: str) -> pd.DataFrame:
        if col not in self.numeric_cols or len(self.df) == 0:
            return pd.DataFrame()
        Q1 = self.df[col].quantile(0.25)
        Q3 = self.df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            return pd.DataFrame()
        return self.df[(self.df[col] < Q1 - 1.5*IQR) | (self.df[col] > Q3 + 1.5*IQR)]

    def correlation_analysis(self) -> pd.DataFrame:
        if len(self.numeric_cols) < 2 or len(self.df) == 0:
            return pd.DataFrame()
        return self.df[self.numeric_cols].corr()

    def generate_insights(self) -> List[Dict[str, str]]:
        insights = []
        if len(self.df) == 0:
            insights.append({
                "type": "warning",
                "title": "Empty Dataset",
                "content": "The dataset contains no rows."
            })
            return insights

        profile = self.get_profile()
        quality = self.data_quality_score()

        if quality["missing_cells"] > 0:
            missing_cols = [c for c, v in profile["missing"].items() if v > 0]
            insights.append({
                "type": "warning",
                "title": "Missing Values Detected",
                "content": f"Found {quality['missing_cells']} missing values in columns: {', '.join(missing_cols[:5])}{'...' if len(missing_cols) > 5 else ''}"
            })
        else:
            insights.append({
                "type": "success",
                "title": "Complete Dataset",
                "content": "No missing values detected. Dataset is complete."
            })

        if quality["duplicate_rows"] > 0:
            insights.append({
                "type": "warning",
                "title": "Duplicate Rows",
                "content": f"Found {quality['duplicate_rows']} duplicate rows ({quality['duplicate_rows']/len(self.df)*100:.1f}% of data)."
            })

        if len(self.numeric_cols) >= 2 and len(self.df) > 1:
            corr = self.correlation_analysis()
            strong_corr = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    val = corr.iloc[i, j]
                    if not pd.isna(val) and abs(val) > 0.7:
                        strong_corr.append((corr.columns[i], corr.columns[j], val))
            if strong_corr:
                for c1, c2, val in strong_corr[:3]:
                    insights.append({
                        "type": "info",
                        "title": f"Strong Correlation: {c1} ↔ {c2}",
                        "content": f"Correlation coefficient: {val:.3f}. These variables move strongly together."
                    })
            weak_corr = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    val = corr.iloc[i, j]
                    if not pd.isna(val) and 0.1 < abs(val) < 0.3:
                        weak_corr.append((corr.columns[i], corr.columns[j], val))
            if weak_corr:
                c1, c2, val = weak_corr[0]
                insights.append({
                    "type": "info",
                    "title": f"Weak Correlation: {c1} ↔ {c2}",
                    "content": f"Correlation coefficient: {val:.3f}. These variables show little linear relationship."
                })

        for col in self.numeric_cols[:3]:
            if self.df[col].notna().sum() > 3:
                skewness = self.df[col].skew()
                if not pd.isna(skewness) and abs(skewness) > 2:
                    insights.append({
                        "type": "warning",
                        "title": f"Skewed Distribution: {col}",
                        "content": f"Skewness: {skewness:.2f}. Data is highly skewed. Consider transformation."
                    })

        for col in self.categorical_cols[:3]:
            vc = self.df[col].value_counts(normalize=True)
            if len(vc) > 0:
                top_pct = vc.iloc[0] * 100
                if top_pct > 80:
                    insights.append({
                        "type": "warning",
                        "title": f"Imbalanced Category: {col}",
                        "content": f"Top category '{vc.index[0]}' represents {top_pct:.1f}% of data."
                    })

        if len(self.df) > 1000:
            insights.append({
                "type": "info",
                "title": "Large Dataset",
                "content": f"Dataset contains {len(self.df):,} rows. Analysis optimized for performance."
            })

        return insights

    def generate_visualizations(self, theme: str = "dark") -> Dict[str, go.Figure]:
        viz = {}
        text_color = '#e0e0ff' if theme == 'dark' else '#302b63'
        bg_color = 'rgba(0,0,0,0)'

        if len(self.df) == 0:
            return viz

        # Missing value heatmap
        if self.df.isnull().sum().sum() > 0:
            missing_df = self.df.isnull().astype(int)
            viz["missing_heatmap"] = px.imshow(
                missing_df.T,
                title="Missing Value Pattern",
                color_continuous_scale=["#2a2a4a", "#ff6b6b"] if theme == 'dark' else ["#e4e8ec", "#e74c3c"],
                height=400
            )
            viz["missing_heatmap"].update_layout(paper_bgcolor=bg_color, plot_bgcolor=bg_color, font_color=text_color)

        # Correlation heatmap
        if len(self.numeric_cols) >= 2 and len(self.df) > 1:
            corr = self.correlation_analysis()
            if not corr.empty:
                viz["correlation"] = px.imshow(
                    corr, text_auto='.2f', aspect="auto",
                    title="Correlation Heatmap",
                    color_continuous_scale="RdBu_r",
                    height=500
                )
                viz["correlation"].update_layout(paper_bgcolor=bg_color, plot_bgcolor=bg_color, font_color=text_color)

        # Numeric distributions
        for col in self.numeric_cols[:5]:
            if self.df[col].notna().sum() > 0:
                fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Box Plot"))
                fig.add_trace(go.Histogram(x=self.df[col].dropna(), name="Histogram", marker_color="#667eea"), row=1, col=1)
                fig.add_trace(go.Box(y=self.df[col].dropna(), name="Box", marker_color="#764ba2"), row=1, col=2)
                fig.update_layout(title_text=f"Distribution: {col}", showlegend=False, height=350,
                                paper_bgcolor=bg_color, plot_bgcolor=bg_color, font_color=text_color)
                viz[f"dist_{col}"] = fig

        # Categorical charts
        for col in self.categorical_cols[:5]:
            counts = self.df[col].value_counts().head(10)
            if len(counts) > 0:
                viz[f"cat_{col}"] = px.bar(
                    x=counts.index, y=counts.values, title=f"Top Categories: {col}",
                    labels={'x': col, 'y': 'Count'}, height=350,
                    color_discrete_sequence=["#667eea"]
                )
                viz[f"cat_{col}"].update_layout(paper_bgcolor=bg_color, plot_bgcolor=bg_color, font_color=text_color)

        # Pair plot for first 4 numeric columns
        if 2 <= len(self.numeric_cols) <= 6 and len(self.df) > 1:
            pair_df = self.df[self.numeric_cols].dropna()
            if len(pair_df) > 0 and len(pair_df.columns) >= 2:
                viz["pairplot"] = px.scatter_matrix(
                    pair_df, title="Pairwise Relationships", height=600,
                    color_discrete_sequence=["#667eea"]
                )
                viz["pairplot"].update_layout(paper_bgcolor=bg_color, plot_bgcolor=bg_color, font_color=text_color)

        # PCA
        if len(self.numeric_cols) >= 3 and len(self.df) > 10:
            df_clean = self.df[self.numeric_cols].dropna()
            if len(df_clean) > 10:
                scaler = StandardScaler()
                scaled = scaler.fit_transform(df_clean)
                pca = PCA(n_components=2)
                pca_result = pca.fit_transform(scaled)
                pca_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])
                viz["pca"] = px.scatter(
                    pca_df, x='PC1', y='PC2',
                    title=f"PCA (Explained Variance: {pca.explained_variance_ratio_.sum():.1%})",
                    height=450, color_discrete_sequence=["#667eea"]
                )
                viz["pca"].update_layout(paper_bgcolor=bg_color, plot_bgcolor=bg_color, font_color=text_color)

        # Clustering
        if len(self.numeric_cols) >= 2 and len(self.df) > 10:
            df_clean = self.df[self.numeric_cols].dropna()
            if len(df_clean) > 10:
                scaler = StandardScaler()
                scaled = scaler.fit_transform(df_clean)
                k = min(3, len(df_clean))
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(scaled)
                cluster_df = pd.DataFrame(scaled[:, :2], columns=['Dim1', 'Dim2'])
                cluster_df['Cluster'] = clusters.astype(str)
                viz["clusters"] = px.scatter(
                    cluster_df, x='Dim1', y='Dim2', color='Cluster',
                    title="K-Means Clustering (2D Projection)", height=450,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                viz["clusters"].update_layout(paper_bgcolor=bg_color, plot_bgcolor=bg_color, font_color=text_color)

        return viz

    def generate_html_report(self, insights: List[Dict], automl_results: Optional[Dict] = None) -> str:
        profile = self.get_profile()
        quality = self.data_quality_score()
        html = f"""<html><head><style>
        body {{ font-family: 'Inter', sans-serif; margin: 40px; background: #f5f7fa; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 16px; margin-bottom: 30px; }}
        .section {{ background: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 0.9rem; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; }}
        .insight {{ padding: 12px; border-left: 4px solid #667eea; background: #f8f9fa; margin: 8px 0; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin: 2px; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        </style></head><body>
        <div class="header">
            <h1>AI Data Scientist Report</h1>
            <p>Dataset: {self.name} | Generated: {pd.Timestamp.now()}</p>
        </div>
        <div class="section">
            <h2>Dataset Overview</h2>
            <div class="metric"><div class="metric-value">{profile['shape'][0]:,}</div><div class="metric-label">Rows</div></div>
            <div class="metric"><div class="metric-value">{profile['shape'][1]}</div><div class="metric-label">Columns</div></div>
            <div class="metric"><div class="metric-value">{quality['overall']}%</div><div class="metric-label">Quality Score</div></div>
        </div>
        <div class="section"><h2>Data Quality</h2>
        <p>Completeness: {quality['completeness']}% | Uniqueness: {quality['uniqueness']}% | Missing Cells: {quality['missing_cells']:,}</p>
        </div>
        <div class="section"><h2>Column Summary</h2><table>
        <tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th></tr>"""
        for col in self.df.columns:
            html += f"<tr><td>{col}</td><td>{profile['dtypes'][col]}</td><td>{profile['missing'][col]} ({profile['missing_pct'][col]}%)</td><td>{profile['unique_values'][col]}</td></tr>"
        html += "</table></div>"
        html += '<div class="section"><h2>Insights</h2>'
        for ins in insights:
            badge_class = f"badge-{ins['type']}"
            html += f'<div class="insight"><span class="badge {badge_class}">{ins["type"].upper()}</span> <strong>{ins["title"]}</strong><br>{ins["content"]}</div>'
        html += "</div>"
        if automl_results:
            html += f'<div class="section"><h2>AutoML Results</h2><pre>{json.dumps(automl_results, indent=2, default=str)}</pre></div>'
        html += "</body></html>"
        return html

    def generate_txt_report(self, insights: List[Dict]) -> str:
        profile = self.get_profile()
        quality = self.data_quality_score()
        lines = [
            "="*60,
            "AI DATA SCIENTIST - ANALYSIS REPORT",
            "="*60,
            f"Dataset: {self.name}",
            f"Generated: {pd.Timestamp.now()}",
            "-"*60,
            "DATASET OVERVIEW",
            f"Rows: {profile['shape'][0]:,}",
            f"Columns: {profile['shape'][1]}",
            f"Memory Usage: {profile.get('memory_usage_mb', 'N/A')} MB",
            "-"*60,
            "DATA QUALITY",
            f"Overall Score: {quality['overall']}/100",
            f"Completeness: {quality['completeness']}%",
            f"Uniqueness: {quality['uniqueness']}%",
            f"Missing Cells: {quality['missing_cells']:,}",
            f"Duplicate Rows: {quality['duplicate_rows']:,}",
            "-"*60,
            "INSIGHTS",
        ]
        for ins in insights:
            lines.append(f"[{ins['type'].upper()}] {ins['title']}")
            lines.append(f"  {ins['content']}")
            lines.append("")
        lines.append("="*60)
        return "\n".join(lines)

    def export_cleaned_data(self) -> pd.DataFrame:
        df_clean = self.df.copy()
        for col in df_clean.columns:
            if df_clean[col].dtype in ['object', 'category']:
                mode_val = df_clean[col].mode()
                fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
                df_clean[col] = df_clean[col].fillna(fill_val)
            else:
                median_val = df_clean[col].median()
                fill_val = median_val if not pd.isna(median_val) else 0
                df_clean[col] = df_clean[col].fillna(fill_val)
        return df_clean
