import json
import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def suggest_chart_type(df: pd.DataFrame, question: str) -> str:
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)
    cat_cols = list(df.select_dtypes(include=["str", "category"]).columns)
    q_lower = question.lower()

    if len(numeric_cols) >= 2 and len(df) > 1:
        if any(w in q_lower for w in ["scatter", "correlation", "relationship", "vs"]):
            return "scatter"
        if any(w in q_lower for w in ["trend", "over time", "time series", "over the"]):
            return "line"
    if cat_cols and numeric_cols:
        if any(w in q_lower for w in ["pie", "proportion", "share", "percentage", "distribution"]):
            return "pie"
        if any(w in q_lower for w in ["bar", "compare", "top", "bottom", "highest", "lowest"]):
            return "bar"
        if any(w in q_lower for w in ["heatmap", "matrix"]):
            return "heatmap"
        return "bar"
    if numeric_cols:
        if any(w in q_lower for w in ["histogram", "distribution", "range"]):
            return "histogram"
        if any(w in q_lower for w in ["box", "outlier"]):
            return "box"
        return "bar"
    return "table"


def build_chart(df: pd.DataFrame, chart_type: str, title: str) -> go.Figure:
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)
    cat_cols = list(df.select_dtypes(include=["str", "category"]).columns)

    if chart_type == "bar" and cat_cols and numeric_cols:
        color_col = cat_cols[0] if len(cat_cols) > 0 else None
        fig = px.bar(df, x=cat_cols[0], y=numeric_cols[0], title=title, color=color_col)
    elif chart_type == "line" and numeric_cols:
        x_col = cat_cols[0] if cat_cols else df.index
        fig = px.line(df, x=x_col, y=numeric_cols, title=title, markers=True)
    elif chart_type == "pie" and cat_cols and numeric_cols:
        fig = px.pie(df, names=cat_cols[0], values=numeric_cols[0], title=title)
    elif chart_type == "scatter" and len(numeric_cols) >= 2:
        fig = px.scatter(
            df, x=numeric_cols[0], y=numeric_cols[1], title=title,
            color=cat_cols[0] if cat_cols else None,
            size=numeric_cols[2] if len(numeric_cols) > 2 else None,
        )
    elif chart_type == "histogram" and numeric_cols:
        fig = px.histogram(df, x=numeric_cols[0], title=title, nbins=20)
    elif chart_type == "box" and numeric_cols:
        fig = px.box(df, y=numeric_cols[0], x=cat_cols[0] if cat_cols else None, title=title)
    elif chart_type == "heatmap" and len(numeric_cols) >= 2 and cat_cols:
        col = cat_cols[1] if len(cat_cols) > 1 else cat_cols[0]
        pivot = df.pivot_table(index=cat_cols[0], columns=col,
                              values=numeric_cols[0], aggfunc="mean")
        fig = px.imshow(pivot, title=title, text_auto=True, aspect="auto")
    else:
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns)),
            cells=dict(values=[df[c] for c in df.columns]),
        )])
        fig.update_layout(title=title)

    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=40, b=40))
    return fig


def figure_to_html(fig: go.Figure) -> str:
    return fig.to_html(include_plotlyjs="cdn", full_html=False)


def figure_to_json(fig: go.Figure) -> dict:
    return json.loads(fig.to_json())
