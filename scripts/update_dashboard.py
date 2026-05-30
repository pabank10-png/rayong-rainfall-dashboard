from __future__ import annotations

import json
import re
import ssl
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "index.html"

RESOURCE_KEY = "cbf94a4c-4d07-4129-8a51-2cb5c9f22fb4"
MODEL_ID = 261334
DATASET_ID = "38d223f7-9c62-48e7-b360-a047cf542069"
QUERY_URL = "https://wabi-south-east-asia-b-primary-api.analysis.windows.net/public/reports/querydata?synchronous=true"
SSL_CONTEXT = ssl._create_unverified_context()
HISTORICAL_START_YEAR_BE = 2513
MONTHS_TH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]

RESERVOIR_DISTRICTS = [
    ("DK", "ดอกกราย", "ระยอง", ["ปลวกแดง"]),
    ("KY", "คลองใหญ่", "ระยอง", ["ปลวกแดง"]),
    ("NPL", "หนองปลาไหล", "ระยอง", ["ปลวกแดง"]),
    ("PS", "ประแสร์", "ชลบุรี", ["บ่อทอง"]),
]


def in_filter(source: str, property_name: str, values: list[int | str]) -> dict[str, Any]:
    encoded = []
    for value in values:
        literal = f"{value}L" if isinstance(value, int) else f"'{value}'"
        encoded.append([{"Literal": {"Value": literal}}])
    return {
        "Condition": {
            "In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": source}}, "Property": property_name}}],
                "Values": encoded,
            }
        }
    }


def build_query(years_be: list[int], province: str) -> dict[str, Any]:
    return {
        "Commands": [{
            "SemanticQueryDataShapeCommand": {
                "Query": {
                    "Version": 2,
                    "From": [{"Name": "m", "Entity": "mRainAmp_TISERVICE", "Type": 0}, {"Name": "mo", "Entity": "month", "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "PROV_T"}, "Name": "mRainAmp_TISERVICE.PROV_T"},
                        {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "AMPHOE_T"}, "Name": "mRainAmp_TISERVICE.AMPHOE_T"},
                        {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "yearBE"}, "Name": "mRainAmp_TISERVICE.yearBE"},
                        {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "MONTH"}, "Name": "mRainAmp_TISERVICE.MONTH"},
                        {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "MEAN_OBS"}}, "Function": 1}, "Name": "Sum(mRainAmp_TISERVICE.MEAN_OBS)"},
                    ],
                    "Where": [in_filter("m", "PROV_T", [province]), in_filter("m", "yearBE", years_be)],
                    "OrderBy": [
                        {"Direction": 1, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "AMPHOE_T"}}},
                        {"Direction": 1, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "yearBE"}}},
                        {"Direction": 1, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "MONTH"}}},
                    ],
                },
                "Binding": {"Primary": {"Groupings": [{"Projections": [0, 1, 2, 3, 4]}]}, "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 5000}}}, "Version": 1},
                "ExecutionMetricsKind": 1,
            }
        }]
    }


def query_powerbi(years_be: list[int], province: str) -> dict[str, Any]:
    body = {
        "version": "1.0.0",
        "queries": [{
            "Query": build_query(years_be, province),
            "ApplicationContext": {"DatasetId": DATASET_ID, "Sources": [{"ReportId": RESOURCE_KEY, "Operation": "VisualContainerRefresh", "VisualId": "githubPagesUpdate"}]},
            "QueryId": "",
        }],
        "cancelQueries": [],
        "modelId": MODEL_ID,
        "userPreferredLocale": "en-US",
    }
    req = urllib.request.Request(
        QUERY_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "ActivityId": "github-pages-rainfall-update",
            "RequestId": f"github-pages-{int(time.time())}",
            "X-PowerBI-ResourceKey": RESOURCE_KEY,
            "User-Agent": "Mozilla/5.0 rainfall-dashboard-updater",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def decode_rows(response: dict[str, Any]) -> list[dict[str, Any]]:
    dsr = response["results"][0]["result"]["data"]["dsr"]
    ds = dsr["DS"][0]
    rows = ds.get("PH", [{}])[0].get("DM0", [])
    dicts = ds.get("ValueDicts", {})
    schema = None
    previous: list[Any] = []
    out = []
    for row in rows:
        if "S" in row:
            schema = row["S"]
        if not schema:
            continue
        values = []
        compressed = row.get("C", [])
        repeat_mask = int(row.get("R", 0))
        c_index = 0
        for idx, column in enumerate(schema):
            if repeat_mask & (1 << idx):
                value = previous[idx]
            else:
                value = compressed[c_index]
                c_index += 1
            dn = column.get("DN")
            if dn and isinstance(value, int):
                value = dicts[dn][value]
            values.append(value)
        previous = values
        out.append({
            "province": values[0],
            "district": values[1],
            "year_be": int(values[2]),
            "month": int(values[3]),
            "rainfall_mm": round(float(values[4]), 3),
        })
    return out


def fetch_rows() -> list[dict[str, Any]]:
    years = list(range(HISTORICAL_START_YEAR_BE, datetime.now().year + 544))
    rows: list[dict[str, Any]] = []
    for province in ["ระยอง", "ชลบุรี"]:
        for start in range(0, len(years), 8):
            rows.extend(decode_rows(query_powerbi(years[start:start + 8], province)))
    return rows


def build_dashboard_data(rows: list[dict[str, Any]]) -> dict[str, dict[int, list[float | None]]]:
    by_key = {(r["province"], r["district"], r["year_be"], r["month"]): r["rainfall_mm"] for r in rows}
    reservoirs: dict[str, dict[int, list[float | None]]] = {"อ่างประแสร์": {}, "3 อ่าง": {}}
    for _, name, province, districts in RESERVOIR_DISTRICTS:
        group = "อ่างประแสร์" if name == "ประแสร์" else "3 อ่าง"
        for year_be in range(HISTORICAL_START_YEAR_BE, datetime.now().year + 544):
            year_ce = year_be - 543
            reservoirs[group].setdefault(year_ce, [None] * 12)
            for month in range(1, 13):
                vals = [by_key[(province, d, year_be, month)] for d in districts if (province, d, year_be, month) in by_key]
                if vals:
                    value = round(sum(vals) / len(vals), 3)
                    if group == "3 อ่าง":
                        reservoirs[group][year_ce][month - 1] = value
                    else:
                        reservoirs[group][year_ce][month - 1] = value
    for group in reservoirs:
        reservoirs[group] = {y: vals for y, vals in reservoirs[group].items() if any(v is not None for v in vals)}
    return reservoirs


def js_data(data: dict[str, dict[int, list[float | None]]]) -> tuple[str, list[int], int, int, int]:
    years = sorted(set(data["3 อ่าง"]) | set(data["อ่างประแสร์"]))
    years = [y for y in years if any((data[g].get(y) or [None] * 12)[m] is not None for g in data for m in range(12))]
    latest_year = max(years)
    latest_month_idx = max(i for i, v in enumerate(data["3 อ่าง"].get(latest_year, [])) if v is not None)
    full_years = [y for y in years if all((data[g].get(y) or [None] * 12)[m] is not None for g in data for m in range(12))]
    last_full = max(full_years)
    chunks = ["const DATA={"]
    for group in ["อ่างประแสร์", "3 อ่าง"]:
        chunks.append(f"  '{group}':{{")
        lines = []
        for y in sorted(data[group]):
            vals = ",".join("null" if v is None else f"{v:g}" for v in data[group][y])
            lines.append(f"    {y}:[{vals}]")
        chunks.append(",\n".join(lines))
        chunks.append("  },")
    chunks[-1] = chunks[-1].rstrip(",")
    chunks.append("};")
    return "\n".join(chunks), years, latest_year, last_full, latest_month_idx


def update_html(data_block: str, years: list[int], current_year: int, last_full: int, current_month_idx: int) -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    html = re.sub(r"const CURRENT_YEAR_CE=\d+,LAST_FULL_YEAR_CE=\d+,CURRENT_MONTH_IDX=\d+;", f"const CURRENT_YEAR_CE={current_year},LAST_FULL_YEAR_CE={last_full},CURRENT_MONTH_IDX={current_month_idx};", html, count=1)
    html = re.sub(r"const DATA=\{[\s\S]*?\n\};\nconst ALL_CE_YEARS=\[[^\]]*\];", data_block + "\nconst ALL_CE_YEARS=[" + ",".join(str(y) for y in years) + "];", html, count=1)
    today = datetime.now()
    today_text = f"{today.day} {MONTHS_TH[today.month - 1]} {today.year + 543}"
    html = re.sub(r"อัปเดต: [^<]+", f"อัปเดต: {today_text}", html, count=1)
    html = re.sub(r"📁 ข้อมูล: \d+–\d+", f"📁 ข้อมูล: {years[0] + 543}–{years[-1] + 543}", html, count=1)
    html = re.sub(r"📌 ปีล่าสุดที่มีข้อมูล: \d+", f"📌 ปีล่าสุดที่มีข้อมูล: {last_full + 543}", html, count=1)
    INDEX_HTML.write_text(html, encoding="utf-8")


def main() -> None:
    data = build_dashboard_data(fetch_rows())
    update_html(*js_data(data))


if __name__ == "__main__":
    main()
