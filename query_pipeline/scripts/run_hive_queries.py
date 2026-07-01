#!/usr/bin/env python3
"""
Run all Hive TPC-DS queries and collect per-query metrics.
"""
import os
import sys
import csv
import time
import glob
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics"))
from yarn_metrics import YarnMetrics

S3_BUCKET = "onpe-datalake-mx"
METRICS_S3_PATH = f"s3://{S3_BUCKET}/query_results/tpc-ds/metrics/hive_metrics.csv"
LOCAL_METRICS_PATH = "/tmp/hive_metrics.csv"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HIVE_DIR = os.path.join(SCRIPT_DIR, "queries", "hive")

METRIC_FIELDS = [
    "engine", "query_name", "status", "start_ts", "end_ts", "wall_time_s",
    "peak_rss_mb", "yarn_app_id", "yarn_elapsed_s", "vcore_seconds",
    "memory_mb_seconds", "allocated_mb", "allocated_vcores", "error",
]


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def list_queries():
    files = sorted(glob.glob(os.path.join(HIVE_DIR, "*.hql")))
    return [(os.path.splitext(os.path.basename(f))[0], f) for f in files]


def write_header_if_needed():
    if not os.path.exists(LOCAL_METRICS_PATH):
        with open(LOCAL_METRICS_PATH, "w", newline="") as fh:
            csv.DictWriter(fh, fieldnames=METRIC_FIELDS).writeheader()


def append_row(row):
    with open(LOCAL_METRICS_PATH, "a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=METRIC_FIELDS).writerow(row)


def run_one(name, path):
    cmd = ["hive", "-f", path]

    log(f"START [hive] {name}")
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
        log(f"SKIP  [hive] {name}: hive binary not found ({exc})")
        return {
            "engine": "hive", "query_name": name, "status": "failed",
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
        "engine": "hive", "query_name": name, "status": status,
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
    log(f"DONE  [hive] {name}: status={status} wall={wall}s "
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
    log("=== TPC-DS Hive Query Benchmark ===")
    write_header_if_needed()

    queries = list_queries()
    if not queries:
        log("ERROR: no .hql query files found.")
        sys.exit(2)

    log(f"Found {len(queries)} Hive queries.")

    rows = []
    for name, path in queries:
        row = run_one(name, path)
        rows.append(row)

    upload_metrics()

    total = len(rows)
    failures = sum(1 for r in rows if r["status"] != "success")
    log(f"=== Hive benchmark complete: {total} runs, {failures} failed ===")
    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
