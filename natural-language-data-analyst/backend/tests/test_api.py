import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-placeholder")

import pandas as pd

from src.analyst.engine import compute_insights
from src.api.schemas import ChartRequest, QueryRequest, SqlValidateResponse
from src.nl2sql.converter import validate_sql
from src.visualization.charts import build_chart, suggest_chart_type


def test_query_request():
    req = QueryRequest(question="show total sales by region", dataset_id="test-id")
    assert req.question == "show total sales by region"
    assert req.dataset_id == "test-id"


def test_chart_request():
    req = ChartRequest(title="Sales Chart", chart_type="bar", dataset_id="test-id")
    assert req.title == "Sales Chart"
    assert req.chart_type == "bar"


def test_sql_validation_passes():
    err = validate_sql("SELECT region, SUM(amount) FROM sales GROUP BY region")
    assert err is None


def test_sql_validation_rejects_dangerous():
    err = validate_sql("DROP TABLE sales")
    assert err is not None
    assert err == "Only SELECT queries are allowed"


def test_sql_validation_rejects_insert():
    err = validate_sql("INSERT INTO sales VALUES (1, 2)")
    assert err is not None


def test_insights_empty_df():
    df = pd.DataFrame()
    result = compute_insights(df, "test question")
    assert result == "No results found."


def test_insights_with_data():
    df = pd.DataFrame({"region": ["East", "West", "East"], "sales": [100, 200, 150]})
    result = compute_insights(df, "show sales")
    assert "Found 3 row(s)" in result
    assert "sales:" in result


def test_suggest_chart_type_bar():
    df = pd.DataFrame({"region": ["A", "B"], "sales": [10, 20]})
    chart = suggest_chart_type(df, "compare sales by region")
    assert chart == "bar"


def test_suggest_chart_type_pie():
    df = pd.DataFrame({"region": ["A", "B"], "sales": [10, 20]})
    chart = suggest_chart_type(df, "show proportion of sales")
    assert chart == "pie"


def test_build_chart():
    df = pd.DataFrame({"region": ["A", "B", "C"], "sales": [10, 20, 30]})
    fig = build_chart(df, "bar", "Test Chart")
    assert fig is not None
    assert fig.layout.title.text == "Test Chart"


def test_sql_validate_response():
    resp = SqlValidateResponse(valid=True, error=None)
    assert resp.valid
    assert resp.error is None


def test_sql_validate_response_invalid():
    resp = SqlValidateResponse(valid=False, error="bad query")
    assert not resp.valid
    assert resp.error == "bad query"
