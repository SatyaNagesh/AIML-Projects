import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def build_dashboard_html(title: str, charts: list[dict]) -> str:
    chart_htmls = []
    for i, c in enumerate(charts):
        chart_htmls.append(
            f'<div class="chart-card" style="grid-column: span {c.get("width", 1)};">'
            f'<h3>{c.get("title", f"Chart {i+1}")}</h3>'
            f'{c.get("html", "")}'
            f"</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#f5f5f5; padding:20px; }}
h1 {{ margin-bottom:20px; color:#333; }}
.grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
.chart-card {{ background:#fff; border-radius:8px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,.1); }}
.chart-card h3 {{ margin-bottom:12px; color:#555; font-size:14px; text-transform:uppercase; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="grid">{"".join(chart_htmls)}</div>
<p style="margin-top:20px;color:#999;font-size:12px">Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</p>
</body>
</html>"""


def build_report_html(title: str, sections: list[dict]) -> str:
    section_htmls = []
    for s in sections:
        if s["type"] == "text":
            section_htmls.append(f'<div class="section"><p>{s["content"]}</p></div>')
        elif s["type"] == "insights":
            section_htmls.append(
                f'<div class="section insights"><pre>{s["content"]}</pre></div>'
            )
        elif s["type"] == "chart":
            section_htmls.append(
                f'<div class="section chart">{s.get("html", "")}</div>'
            )
        elif s["type"] == "table":
            section_htmls.append(
                f'<div class="section table">{s.get("html", "")}</div>'
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#fff; padding:40px; max-width:960px; margin:0 auto; }}
h1 {{ margin-bottom:8px; color:#222; }}
.meta {{ color:#888; font-size:13px; margin-bottom:30px; }}
.section {{ margin-bottom:24px; }}
.section p {{ line-height:1.7; color:#444; }}
.insights pre {{ background:#f8f8f8; padding:16px; border-radius:6px; font-size:13px; line-height:1.6; overflow-x:auto; }}
.chart {{ background:#fafafa; padding:12px; border-radius:8px; }}
.table table {{ border-collapse:collapse; width:100%; }}
.table th,.table td {{ border:1px solid #ddd; padding:8px; text-align:left; }}
.table th {{ background:#f0f0f0; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</p>
{"".join(section_htmls)}
</body>
</html>"""
