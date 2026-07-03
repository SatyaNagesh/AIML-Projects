import logging
import re

from src.llm.client import chat

logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = frozenset({
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "EXEC",
})


def build_schema_section(column_info: list[dict], table_name: str) -> str:
    cols = "\n".join(
        f"  - {c['name']} ({c['type']})"
        + (
            f"  e.g. {', '.join(str(v) for v in c.get('sample_values', [])[:3])}"
            if c.get("sample_values") else ""
        )
        for c in column_info
    )
    return f"Table: {table_name}\nColumns:\n{cols}"


def validate_sql(sql: str) -> str | None:
    stripped = sql.strip().rstrip(";")
    upper = stripped.upper()

    if not upper.startswith("SELECT"):
        return "Only SELECT queries are allowed"

    for kw in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{kw}\b"
        if re.search(pattern, upper) and kw != "SELECT":
            return f"Query contains forbidden keyword: {kw}"

    return None


async def generate_sql(question: str, column_info: list[dict], table_name: str) -> str:
    schema = build_schema_section(column_info, table_name)
    system_prompt = (
        "You are a PostgreSQL expert. Convert natural language questions into SQL queries.\n\n"
        f"Schema:\n{schema}\n\n"
        "Rules:\n"
        "- Return ONLY the raw SQL query, no markdown, no backticks, no explanations\n"
        "- Use only SELECT statements\n"
        "- Never use DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, EXEC\n"
        "- Use proper PostgreSQL syntax\n"
        "- Use aliases for readability where appropriate\n"
        "- For aggregations, always include GROUP BY with the non-aggregated columns"
    )

    sql = await chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ], temperature=0.05, max_tokens=1000)

    sql = sql.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()
    return sql
