#!/usr/bin/env python3
"""
TPC-DS query benchmark orchestrator.

Runs the 9 analytical queries on BOTH Spark and Hive (one query per file),
captures per-query metrics (wall time, peak RSS, YARN vcore/memory seconds),
writes a local CSV incrementally (resilient to mid-run crashes) and uploads
the final metrics CSV to S3.

Per-query isolation: a failure is recorded and the run continues. The script
exits non-zero only if at least one query failed, so EMR marks the step failed
and terminates the cluster (cost safety).

Fairness: query order is fixed; for each query the two engines run back to
back. The engine that runs first alternates per query so neither engine
systematically benefits from warm OS page cache.

Run on the EMR master node (where `hive` and `spark-sql` are on PATH):
    python3 run_queries.py
"""
import os
import sys
import csv
import time
import glob
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics"))
from yarn_metrics import YarnMetrics  # noqa: E402

S3_BUCKET = "onpe-datalake-mx"
QUERY_RESULTS_BASE = f"s3://{S3_BUCKET}/query_results/tpc-ds"
METRICS_S3_PATH = f"{QUERY_RESULTS_BASE}/metrics/query_metrics.csv"
LOCAL_METRICS_PATH = "/tmp/query_metrics.csv"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPARK_DIR = os.path.join(SCRIPT_DIR, "queries", "spark")
HIVE_DIR = os.path.join(SCRIPT_DIR, "queries", "hive")

METRIC_FIELDS = [
    "engine", "query_name", "status", "start_ts", "end_ts", "wall_time_s",
    "peak_rss_mb", "yarn_app_id", "yarn_elapsed_s", "vcore_seconds",
    "memory_mb_seconds", "allocated_mb", "allocated_vcores", "error",
]

SPARK_ARGS = [
    "spark-sql",
    "--master", "yarn",
    "--deploy-mode", "client",
    "--executor-memory", "4g",
    "--num-executors", "4",
    "--conf", "spark.sql.adaptive.enabled=true",
    "--conf", "spark.sql.adaptive.coalescePartitions.enabled=true",
    "--conf", "spark.sql.adaptive.skewJoin.enabled=true",
    "--conf", "spark.sql.optimizer.dynamicPartitionPruning.enabled=true",
    "--conf", "spark.sql.autoBroadcastJoinThreshold=104857600",
    "--conf", "spark.sql.parquet.filterPushdown=true",
    "--conf", "spark.sql.parquet.enableVectorizedReader=true",
]


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def list_queries(directory, ext):
    files = sorted(glob.glob(os.path.join(directory, f"*.{ext}")))
    return [(os.path.splitext(os.path.basename(f))[0], f) for f in files]


def write_header_if_needed():
    if not os.path.exists(LOCAL_METRICS_PATH):
        with open(LOCAL_METRICS_PATH, "w", newline="") as fh:
            csv.DictWriter(fh, fieldnames=METRIC_FIELDS).writeheader()


def append_row(row):
    with open(LOCAL_METRICS_PATH, "a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=METRIC_FIELDS).writerow(row)


def run_one(engine, name, path):
    """Run a single query on the given engine and return a metrics row dict."""
    if engine == "spark":
        cmd = SPARK_ARGS + ["-f", path]
    else:
        cmd = ["hive", "-f", path]

    log(f"START [{engine}] {name}")
    start_ts = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()

    ym = YarnMetrics()
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError as exc:
        wall = round(time.perf_counter() - t0, 3)
        end_ts = datetime.now(timezone.utc).isoformat()
        log(f"SKIP  [{engine}] {name}: engine binary not found ({exc})")
        return {
            "engine": engine, "query_name": name, "status": "failed",
            "start_ts": start_ts, "end_ts": end_ts, "wall_time_s": wall,
            "peak_rss_mb": "", "yarn_app_id": "", "yarn_elapsed_s": "",
            "vcore_seconds": "", "memory_mb_seconds": "", "allocated_mb": "",
            "allocated_vcores": "", "error": f"binary not found: {exc}",
        }

    ym.attach(proc.pid)
    out, _ = proc.communicate()
    rc = proc.returncode
    yarn_m = ym.finalize(out or "")
    wall = round(time.perf_counter() - t0, 3)
    end_ts = datetime.now(timezone.utc).isoformat()

    status = "success" if rc == 0 else "failed"
    err = ""
    if rc != 0:
        tail = (out or "").strip().splitlines()[-15:]
        err = " | ".join(tail)[:3000]

    row = {
        "engine": engine, "query_name": name, "status": status,
        "start_ts": start_ts, "end_ts": end_ts, "wall_time_s": wall,
        "peak_rss_mb": yarn_m.get("peak_rss_mb", ""),
        "yarn_app_id": yarn_m.get("yarn_app_id", ""),
        "yarn_elapsed_s": yarn_m.get("yarn_elapsed_s", ""),
        "vcore_seconds": yarn_m.get("vcore_seconds", ""),
        "memory_mb_seconds": yarn_m.get("memory_mb_seconds", ""),
        "allocated_mb": yarn_m.get("allocated_mb", ""),
        "allocated_vcores": yarn_m.get("allocated_vcores", ""),
        "error": err,
    }
    append_row(row)
    log(f"DONE  [{engine}] {name}: status={status} wall={wall}s "
        f"vcore_s={row['vcore_seconds']} memMBs={row['memory_mb_seconds']} "
        f"peakRss={row['peak_rss_mb']}MB app={row['yarn_app_id']}")
    return row


def upload_metrics():
    if not os.path.exists(LOCAL_METRICS_PATH):
        log("No metrics file to upload.")
        return
    log(f"Uploading metrics to {METRICS_S3_PATH}")
    try:
        subprocess.run(
            ["aws", "s3", "cp", LOCAL_METRICS_PATH, METRICS_S3_PATH],
            check=True, capture_output=True, text=True,
        )
        log("Metrics uploaded.")
    except subprocess.CalledProcessError as exc:
        log(f"WARN: metrics upload failed: {exc.stderr.strip()}")


def main():
    log("=== TPC-DS Query Benchmark: Spark vs Hive ===")
    write_header_if_needed()

    spark_queries = list_queries(SPARK_DIR, "sql")
    hive_queries = list_queries(HIVE_DIR, "hql")

    if not spark_queries and not hive_queries:
        log("ERROR: no query files found.")
        sys.exit(2)

    log(f"Found {len(spark_queries)} Spark queries and {len(hive_queries)} Hive queries.")

    # Pair queries by name; iterate queries in sorted order.
    spark_map = dict(spark_queries)
    hive_map = dict(hive_queries)
    all_names = sorted(set(spark_map) | set(hive_map))

    rows = []
    for idx, name in enumerate(all_names):
        # Alternate which engine runs first to balance cold/warm cache effects.
        engines = ["spark", "hive"] if idx % 2 == 0 else ["hive", "spark"]
        for engine in engines:
            src = spark_map.get(name) if engine == "spark" else hive_map.get(name)
            if src is None:
                log(f"SKIP  [{engine}] {name}: no file for this engine")
                continue
            row = run_one(engine, name, src)
            rows.append(row)

    upload_metrics()

    total = len(rows)
    failures = sum(1 for r in rows if r["status"] != "success")
    log(f"=== Benchmark complete: {total} runs, {failures} failed ===")
    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
