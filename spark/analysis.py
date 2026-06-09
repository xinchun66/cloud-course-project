import sys
import time
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, isnan, mean, stddev, when


def missing_count(column_name):
    value = col(column_name)
    if column_name in {"year", "rating_score", "rating_count", "collect_count"}:
        return count(when(value.isNull() | isnan(value), column_name))
    return count(when(value.isNull() | (value == ""), column_name))


def print_missing_ratios(df, title):
    total = df.count()
    print(f"\n===== {title} missing value ratio =====")
    print(f"total rows: {total}")

    if total == 0:
        print("DataFrame is empty.")
        return

    missing_exprs = [
        missing_count(column_name).alias(column_name)
        for column_name in df.columns
    ]
    missing_row = df.select(missing_exprs).first().asDict()

    for column_name in df.columns:
        missing = missing_row[column_name]
        ratio = missing / total
        print(f"{column_name}: {missing} / {total} = {ratio:.2%}")


def print_numeric_statistics(df, title):
    numeric_columns = ["year", "rating_score", "rating_count", "collect_count"]

    print(f"\n===== {title} numeric statistics =====")
    df.select(numeric_columns).summary("count", "mean", "stddev", "min", "max").show(
        truncate=False
    )

    print("\nDetailed statistics:")
    df.select(
        *[
            mean(col(column_name)).alias(f"{column_name}_mean")
            for column_name in numeric_columns
        ],
        *[
            stddev(col(column_name)).alias(f"{column_name}_stddev")
            for column_name in numeric_columns
        ],
    ).show(truncate=False)


def show_sql_result(spark, title, query, analysis, rows=20):
    print(f"\n===== A-2 {title} =====")
    result_df = spark.sql(query)
    result_df.show(rows, truncate=False)
    print(f"Analysis: {analysis}")
    return result_df


def run_spark_sql_analysis(spark, cleaned_df):
    cleaned_df.createOrReplaceTempView("cleaned_movies")

    spark.sql(
        """
        CREATE OR REPLACE TEMP VIEW movie_genres AS
        SELECT
            movie_id,
            title,
            year,
            rating_score,
            rating_count,
            collect_count,
            trim(genre) AS genre
        FROM cleaned_movies
        LATERAL VIEW explode(split(genres, '/')) genre_table AS genre
        WHERE genres <> 'Unknown'
        """
    )

    spark.sql(
        """
        CREATE OR REPLACE TEMP VIEW movie_countries AS
        SELECT
            movie_id,
            title,
            year,
            rating_score,
            rating_count,
            collect_count,
            trim(country) AS country
        FROM cleaned_movies
        LATERAL VIEW explode(split(countries, '/')) country_table AS country
        WHERE countries <> 'Unknown'
        """
    )

    show_sql_result(
        spark,
        "Query 1 - GROUP BY genre rating summary",
        """
        SELECT
            genre,
            COUNT(*) AS movie_count,
            ROUND(AVG(rating_score), 2) AS avg_rating,
            ROUND(AVG(rating_count), 0) AS avg_rating_count
        FROM movie_genres
        GROUP BY genre
        HAVING COUNT(*) >= 5
        ORDER BY avg_rating DESC, movie_count DESC
        LIMIT 15
        """,
        "This query groups films by genre and compares average scores and audience scale. "
        "It helps identify which genres keep stable high ratings instead of only relying "
        "on a single famous movie, so it is useful for explaining taste differences.",
    )

    show_sql_result(
        spark,
        "Query 2 - ORDER BY Top-N popular movies",
        """
        SELECT
            title,
            year,
            rating_score,
            rating_count,
            collect_count,
            genres
        FROM cleaned_movies
        ORDER BY rating_count DESC
        LIMIT 10
        """,
        "This Top-N query ranks movies by rating_count, which reflects how widely each "
        "movie was evaluated by users. The result usually favors classic and highly "
        "visible films, making it different from simply sorting by rating_score.",
    )

    show_sql_result(
        spark,
        "Query 3 - yearly rating trend",
        """
        SELECT
            year,
            COUNT(*) AS movie_count,
            ROUND(AVG(rating_score), 2) AS avg_rating,
            ROUND(AVG(rating_count), 0) AS avg_rating_count
        FROM cleaned_movies
        WHERE year BETWEEN 1900 AND 2030
        GROUP BY year
        HAVING COUNT(*) >= 3
        ORDER BY year
        """,
        "This time trend query summarizes movies by release year. It can show whether "
        "older or newer movies have different average ratings, while the movie_count "
        "column reminds us that years with fewer records are less statistically stable.",
        rows=30,
    )

    show_sql_result(
        spark,
        "Query 4 - window function country ranking",
        """
        SELECT
            country,
            rank_in_country,
            title,
            year,
            rating_score,
            rating_count
        FROM (
            SELECT
                country,
                title,
                year,
                rating_score,
                rating_count,
                ROW_NUMBER() OVER (
                    PARTITION BY country
                    ORDER BY rating_score DESC, rating_count DESC
                ) AS rank_in_country
            FROM movie_countries
        ) ranked
        WHERE rank_in_country <= 3
        ORDER BY country, rank_in_country
        """,
        "This window-function query ranks movies inside each country or region instead "
        "of ranking the whole dataset together. It keeps local comparison fairer, because "
        "films from smaller markets are not completely hidden by globally popular movies.",
        rows=60,
    )


def run_performance_comparison(spark, input_path, cleaned_df):
    print("\n===== A-3 Performance comparison and Amdahl analysis =====")

    executor_instances = spark.conf.get("spark.executor.instances", "local")

    query = """
        SELECT
            genre,
            COUNT(*) AS movie_count,
            ROUND(AVG(rating_score), 2) AS avg_rating,
            ROUND(AVG(rating_count), 0) AS avg_rating_count
        FROM movie_genres
        GROUP BY genre
        HAVING COUNT(*) >= 5
        ORDER BY avg_rating DESC, movie_count DESC
    """

    spark_start = time.perf_counter()
    spark_result = spark.sql(query)
    spark_rows = spark_result.collect()
    spark_seconds = time.perf_counter() - spark_start

    print(f"Spark executor instances: {executor_instances}")
    print(f"PySpark query time: {spark_seconds:.4f} seconds")
    print(f"PySpark result rows: {len(spark_rows)}")

    pandas_seconds = None
    try:
        import pandas as pd

        pandas_start = time.perf_counter()
        pandas_df = pd.read_csv(input_path)
        pandas_df = pandas_df.dropna(
            subset=["movie_id", "title", "year", "rating_score", "rating_count"]
        )
        pandas_df["genres"] = pandas_df["genres"].fillna("Unknown")
        pandas_df = pandas_df[pandas_df["genres"] != "Unknown"]
        pandas_df = pandas_df.assign(genre=pandas_df["genres"].str.split("/")).explode(
            "genre"
        )
        pandas_df["genre"] = pandas_df["genre"].str.strip()
        pandas_result = (
            pandas_df.groupby("genre")
            .agg(
                movie_count=("movie_id", "count"),
                avg_rating=("rating_score", "mean"),
                avg_rating_count=("rating_count", "mean"),
            )
            .query("movie_count >= 5")
            .sort_values(["avg_rating", "movie_count"], ascending=[False, False])
        )
        pandas_result["avg_rating"] = pandas_result["avg_rating"].round(2)
        pandas_result["avg_rating_count"] = pandas_result["avg_rating_count"].round(0)
        pandas_seconds = time.perf_counter() - pandas_start

        print(f"Pandas query time: {pandas_seconds:.4f} seconds")
        print(f"Pandas result rows: {len(pandas_result)}")
    except Exception as exc:
        print(f"Pandas comparison skipped: {exc}")

    if pandas_seconds and spark_seconds > 0:
        speedup = pandas_seconds / spark_seconds
        parallel_fraction = None
        if executor_instances not in {"local", "0", ""}:
            workers = int(executor_instances)
            if workers > 1 and speedup > 0:
                parallel_fraction = (1 - 1 / speedup) / (1 - 1 / workers)

        print("\nPerformance table:")
        print("method,executor_instances,time_seconds,speedup_vs_pandas")
        print(f"Pandas,1,{pandas_seconds:.4f},1.0000")
        print(f"PySpark,{executor_instances},{spark_seconds:.4f},{speedup:.4f}")

        if parallel_fraction is not None:
            print(f"Estimated parallel fraction f: {parallel_fraction:.4f}")
            print(
                "Amdahl analysis: speedup is limited by serial work, task startup, "
                "CSV parsing, shuffle communication, serialization, and the fact that "
                "this dataset may be too small to fully amortize distributed overhead."
            )
        else:
            print(
                "Amdahl analysis: run this script twice in SparkApplication, once with "
                "executor.instances=1 and once with executor.instances=2, then compare "
                "the two PySpark times with the Pandas time in the report."
            )

        write_performance_outputs(
            executor_instances, pandas_seconds, spark_seconds, speedup
        )
        write_amdahl_outputs()


def write_performance_outputs(executor_instances, pandas_seconds, spark_seconds, speedup):
    output_dir = Path("figures")
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / f"a3_performance_exec_{executor_instances}.csv"
    csv_path.write_text(
        "method,executor_instances,time_seconds,speedup_vs_pandas\n"
        f"Pandas,1,{pandas_seconds:.4f},1.0000\n"
        f"PySpark,{executor_instances},{spark_seconds:.4f},{speedup:.4f}\n",
        encoding="utf-8",
    )
    print(f"Saved performance CSV: {csv_path}")

    try:
        import matplotlib.pyplot as plt

        methods = ["Pandas", f"PySpark exec={executor_instances}"]
        times = [pandas_seconds, spark_seconds]
        plt.figure(figsize=(8, 5))
        bars = plt.bar(methods, times, color=["#4c78a8", "#f58518"])
        plt.ylabel("Time / seconds")
        plt.title("A-3 Pandas vs PySpark Performance")
        for bar, value in zip(bars, times):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.2f}s",
                ha="center",
                va="bottom",
            )
        plt.tight_layout()
        chart_path = output_dir / f"a3_performance_exec_{executor_instances}.png"
        plt.savefig(chart_path, dpi=160)
        plt.close()
        print(f"Saved performance chart: {chart_path}")
    except Exception as exc:
        print(f"Chart generation skipped: {exc}")


def read_performance_csv(path):
    rows = path.read_text(encoding="utf-8").strip().splitlines()[1:]
    result = {}
    for row in rows:
        method, executor_instances, time_seconds, speedup_vs_pandas = row.split(",")
        result[(method, executor_instances)] = {
            "time_seconds": float(time_seconds),
            "speedup_vs_pandas": float(speedup_vs_pandas),
        }
    return result


def write_amdahl_outputs():
    output_dir = Path("figures")
    exec1_path = output_dir / "a3_performance_exec_1.csv"
    exec2_path = output_dir / "a3_performance_exec_2.csv"

    if not exec1_path.exists() or not exec2_path.exists():
        print(
            "Amdahl summary skipped: run once with executor.instances=1 and once "
            "with executor.instances=2 to generate both performance CSV files."
        )
        return

    exec1_data = read_performance_csv(exec1_path)
    exec2_data = read_performance_csv(exec2_path)
    pandas_time = exec1_data[("Pandas", "1")]["time_seconds"]
    spark_exec1_time = exec1_data[("PySpark", "1")]["time_seconds"]
    spark_exec2_time = exec2_data[("PySpark", "2")]["time_seconds"]

    measured_speedup_exec2 = spark_exec1_time / spark_exec2_time
    parallel_fraction = (1 - 1 / measured_speedup_exec2) / (1 - 1 / 2)
    parallel_fraction = max(0.0, min(1.0, parallel_fraction))
    amdahl_exec1 = 1.0
    amdahl_exec2 = 1 / ((1 - parallel_fraction) + parallel_fraction / 2)

    summary_path = output_dir / "a3_amdahl_summary.csv"
    summary_path.write_text(
        "method,workers,time_seconds,measured_speedup,amdahl_theory_speedup\n"
        f"Pandas,1,{pandas_time:.4f},1.0000,\n"
        f"PySpark,1,{spark_exec1_time:.4f},1.0000,{amdahl_exec1:.4f}\n"
        f"PySpark,2,{spark_exec2_time:.4f},{measured_speedup_exec2:.4f},"
        f"{amdahl_exec2:.4f}\n"
        f"parallel_fraction_f,,,{parallel_fraction:.4f},\n",
        encoding="utf-8",
    )
    print(f"Saved Amdahl summary CSV: {summary_path}")
    print(f"Measured PySpark speedup from 1 to 2 executors: {measured_speedup_exec2:.4f}")
    print(f"Estimated parallel fraction f: {parallel_fraction:.4f}")

    try:
        import matplotlib.pyplot as plt

        workers = [1, 2]
        measured = [1.0, measured_speedup_exec2]
        theory = [amdahl_exec1, amdahl_exec2]
        plt.figure(figsize=(8, 5))
        plt.plot(workers, measured, marker="o", label="Measured speedup")
        plt.plot(workers, theory, marker="s", label="Amdahl theory")
        plt.xticks(workers)
        plt.xlabel("PySpark executor instances")
        plt.ylabel("Speedup")
        plt.title("A-3 Measured Speedup vs Amdahl Theory")
        plt.legend()
        plt.tight_layout()
        chart_path = output_dir / "a3_amdahl_speedup.png"
        plt.savefig(chart_path, dpi=160)
        plt.close()
        print(f"Saved Amdahl chart: {chart_path}")
    except Exception as exc:
        print(f"Amdahl chart generation skipped: {exc}")


def main():
    spark = (
        SparkSession.builder.appName("DoubanMovieCleaning")
        .config("spark.sql.session.timeZone", "Asia/Shanghai")
        .getOrCreate()
    )

    input_path = sys.argv[1] if len(sys.argv) > 1 else "douban_movies.csv"

    print(f"Input path: {input_path}")

    raw_df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .option("multiLine", True)
        .option("escape", '"')
        .csv(input_path)
    )

    print("\n===== Raw schema =====")
    raw_df.printSchema()

    print("\n===== Raw top 5 rows =====")
    raw_df.show(5, truncate=40)

    before_count = raw_df.count()
    print_missing_ratios(raw_df, "Before cleaning")
    print_numeric_statistics(raw_df, "Before cleaning")

    # Strategy 1: drop rows missing key analytical fields.
    cleaned_df = raw_df.dropna(
        subset=["movie_id", "title", "year", "rating_score", "rating_count"]
    )

    # Strategy 2: fill missing optional text fields with clear placeholders.
    cleaned_df = cleaned_df.fillna(
        {
            "original_title": "Unknown",
            "genres": "Unknown",
            "countries": "Unknown",
            "directors": "Unknown",
            "summary": "No summary",
        }
    )

    cleaned_df = cleaned_df.withColumn("year", col("year").cast("int"))

    after_count = cleaned_df.count()
    print("\n===== Row count comparison =====")
    print(f"before cleaning: {before_count}")
    print(f"after cleaning: {after_count}")
    print(f"removed rows: {before_count - after_count}")

    print_missing_ratios(cleaned_df, "After cleaning")
    print_numeric_statistics(cleaned_df, "After cleaning")

    print("\n===== Cleaned top 5 rows =====")
    cleaned_df.show(5, truncate=40)

    run_spark_sql_analysis(spark, cleaned_df)
    run_performance_comparison(spark, input_path, cleaned_df)

    spark.stop()


if __name__ == "__main__":
    main()
