import csv
import math
from collections import OrderedDict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "douban_movies.csv"
OUT_DIR = ROOT / "figures_B"

NUMERIC_COLUMNS = {"year", "rating_score", "rating_count", "collect_count"}
KEY_COLUMNS = ["movie_id", "title", "year", "rating_score", "rating_count"]
FILL_COLUMNS = {
    "original_title": "Unknown",
    "genres": "Unknown",
    "countries": "Unknown",
    "directors": "Unknown",
    "summary": "No summary",
}


def load_font(size):
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/Consola.ttf"),
        Path("C:/Windows/Fonts/simhei.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


FONT = load_font(22)
TITLE_FONT = load_font(28)
SMALL_FONT = load_font(18)


def is_missing(value):
    return value is None or value == ""


def to_number(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except ValueError:
        return None


def infer_type(values):
    seen = [value for value in values if not is_missing(value)]
    if not seen:
        return "string"
    numeric = [to_number(value) for value in seen]
    if all(value is not None for value in numeric):
        if all(float(value).is_integer() for value in numeric):
            return "integer"
        return "double"
    return "string"


def read_rows():
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    return reader.fieldnames or [], rows


def cleaned_rows(rows):
    result = []
    for row in rows:
        if any(is_missing(row.get(column)) for column in KEY_COLUMNS):
            continue
        cleaned = dict(row)
        for column, fill in FILL_COLUMNS.items():
            if is_missing(cleaned.get(column)):
                cleaned[column] = fill
        result.append(cleaned)
    return result


def text_width(draw, text, font=FONT):
    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return right - left


def draw_lines(path, title, lines, width=1500, margin=44):
    line_height = 34
    height = margin * 2 + 48 + line_height * len(lines)
    image = Image.new("RGB", (width, max(height, 520)), "#f8fafc")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, image.height), fill="#f8fafc")
    draw.text((margin, margin), title, fill="#111827", font=TITLE_FONT)
    y = margin + 58
    for line in lines:
        draw.text((margin, y), line, fill="#111827", font=FONT)
        y += line_height
    image.save(path)


def draw_table(path, title, headers, rows, width=1700, margin=40):
    draw_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    col_widths = []
    for index, header in enumerate(headers):
        values = [str(row[index]) for row in rows]
        max_width = max([text_width(draw_probe, str(header), FONT)] + [text_width(draw_probe, value, FONT) for value in values])
        col_widths.append(min(max_width + 34, 360))
    table_width = sum(col_widths)
    width = max(width, table_width + margin * 2)
    row_height = 42
    height = margin * 2 + 58 + row_height * (len(rows) + 1)
    image = Image.new("RGB", (width, max(height, 520)), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.text((margin, margin), title, fill="#111827", font=TITLE_FONT)
    y = margin + 62
    x = margin
    for header, col_width in zip(headers, col_widths):
        draw.rectangle((x, y, x + col_width, y + row_height), fill="#e5e7eb", outline="#cbd5e1")
        draw.text((x + 12, y + 9), str(header)[:28], fill="#111827", font=SMALL_FONT)
        x += col_width
    y += row_height
    for row in rows:
        x = margin
        for value, col_width in zip(row, col_widths):
            draw.rectangle((x, y, x + col_width, y + row_height), fill="#ffffff", outline="#e5e7eb")
            value = str(value).replace("\n", " ")
            if len(value) > 30:
                value = value[:27] + "..."
            draw.text((x + 12, y + 9), value, fill="#111827", font=SMALL_FONT)
            x += col_width
        y += row_height
    image.save(path)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    headers, rows = read_rows()
    cleaned = cleaned_rows(rows)

    samples = {column: [row.get(column, "") for row in rows[:5000]] for column in headers}
    schema_lines = ["root"]
    for column in headers:
        schema_lines.append(f" |-- {column}: {infer_type(samples[column])} (nullable = true)")
    draw_lines(OUT_DIR / "a1-schema.png", "Raw schema", schema_lines, width=1200)

    top_headers = ["movie_id", "title", "year", "rating_score", "rating_count", "genres", "countries"]
    top_rows = [[row.get(column, "") for column in top_headers] for row in rows[:5]]
    draw_table(OUT_DIR / "a1-top5.png", "Raw top 5 rows", top_headers, top_rows)

    total = len(rows)
    ratio_rows = []
    for column in headers:
        missing = sum(1 for row in rows if is_missing(row.get(column)))
        ratio_rows.append([column, missing, total, f"{missing / total:.2%}"])
    draw_table(OUT_DIR / "a1-missing-ratio.png", "Before cleaning missing value ratio", ["column", "missing", "total", "ratio"], ratio_rows, width=1100)

    before_count = len(rows)
    after_count = len(cleaned)
    removed = before_count - after_count
    draw_table(
        OUT_DIR / "a1-row-count-comparison.png",
        "Row count comparison",
        ["stage", "records"],
        [["before cleaning", before_count], ["after cleaning", after_count], ["removed rows", removed]],
        width=900,
    )

    stats = []
    for column in ["year", "rating_score", "rating_count", "collect_count"]:
        values = [to_number(row.get(column)) for row in cleaned]
        values = [value for value in values if value is not None]
        count = len(values)
        mean = sum(values) / count if count else math.nan
        variance = sum((value - mean) ** 2 for value in values) / (count - 1) if count > 1 else 0
        stddev = math.sqrt(variance)
        stats.append([column, count, f"{mean:.4f}", f"{stddev:.4f}", f"{min(values):.0f}", f"{max(values):.0f}"])
    draw_table(
        OUT_DIR / "a1-statistics-summary.png",
        "After cleaning numeric statistics",
        ["column", "count", "mean", "stddev", "min", "max"],
        stats,
        width=1250,
    )


if __name__ == "__main__":
    main()
