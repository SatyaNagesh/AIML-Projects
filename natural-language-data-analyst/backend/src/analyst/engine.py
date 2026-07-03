import logging

import pandas as pd
from sqlalchemy import text as sa_text

from src.db.database import async_session_factory

logger = logging.getLogger(__name__)


async def execute_sql(sql: str) -> pd.DataFrame:
    async with async_session_factory() as session:
        result = await session.execute(sa_text(sql))
        rows = result.fetchall()
        cols = result.keys()
        return pd.DataFrame(rows, columns=cols)


def compute_insights(df: pd.DataFrame, question: str) -> str:
    if df.empty:
        return "No results found."

    parts: list[str] = [f"Found {len(df)} row(s) with {len(df.columns)} column(s)."]

    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        parts.append(
            f"- {col}: min={series.min():.2f}, max={series.max():.2f}, "
            f"mean={series.mean():.2f}, median={series.median():.2f}"
        )

    for col in df.columns:
        if df[col].dtype.name in ("str", "string", "category"):
            top = df[col].value_counts().head(5)
            vals_str = ", ".join(f"{k} ({v})" for k, v in top.items())
            parts.append(f"- Top values in '{col}': {vals_str}")

    return "\n".join(parts)
