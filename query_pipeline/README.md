# TPC-DS Query & Metrics Pipeline (Spark vs Hive)

Runs 9 analytical queries on **both** Apache Spark and Apache Hive (on Tez)
over the TPC-DS Parquet warehouse produced by the root `main.tf`, captures
per-query performance metrics, and writes results + a metrics CSV to S3.

This is an independent, self-contained Terraform root module. It does **not**
modify the data-generation pipeline in the repo root.

## Prerequisites

- The root `main.tf` must have run first: 10 GB of TPC-DS data exists as
  partitioned Parquet at `s3://onpe-datalake-mx/warehouse/tpcds-10gb/`.
- AWS Learner Lab roles `LabRole` (service) and `LabInstanceProfile` (EC2)
  must exist (they do in the Learner Lab account).
- Terraform + the AWS provider cache (already present in the repo).

## Run

```bash
cd query_pipeline
terraform init
terraform apply
```

The EMR cluster auto-terminates when all steps finish (or on step failure).
Monitor progress in the EMR console or via the step logs at
`s3://onpe-datalake-mx/emr-logs/`.

## Outputs

```
s3://onpe-datalake-mx/query_results/tpc-ds/
├── spark/<query_name>/part-*.csv      # CSV with header (Spark INSERT OVERWRITE DIRECTORY)
├── hive/<query_name>/part-*.csv       # comma-delimited, no header (Hive)
└── metrics/query_metrics.csv          # per-query benchmark metrics
```

### Metrics CSV columns

| column | meaning |
|---|---|
| `engine` | `spark` or `hive` |
| `query_name` | e.g. `01_top_customers_by_purchases` |
| `status` | `success` / `failed` |
| `start_ts`, `end_ts` | UTC ISO-8601 timestamps |
| `wall_time_s` | end-to-end wall clock (Python `perf_counter`) |
| `peak_rss_mb` | peak RSS of the engine subprocess tree (`psutil`) |
| `yarn_app_id` | YARN application id |
| `yarn_elapsed_s` | YARN-reported elapsed time (ms → s reported as-is by YARN) |
| `vcore_seconds` | YARN `vcoreSeconds` (total virtual CPU-seconds consumed) |
| `memory_mb_seconds` | YARN `memorySeconds` (total MB-seconds consumed) |
| `allocated_mb` / `allocated_vcores` | resources allocated to the app |
| `error` | last log lines if failed, else empty |

> **Note:** `yarn_elapsed_s` is the raw YARN `elapsedTime` field (milliseconds).
> `wall_time_s` includes engine startup/JVM/Tez-session overhead and is the
> number to use for end-user latency comparisons.

## Architecture

```
Terraform (main.tf)
  └─ aws_s3_object.query_scripts   uploads scripts/** → S3 (etag-tracked)
  └─ aws_emr_cluster.tpcds_queries  Hadoop + Spark + Hive + Tez, m4.large x5
       ├─ Step 1 Stage_Scripts          copy scripts to /tmp + pip install psutil
       ├─ Step 2 Create_Hive_Tables     hive -f tpcds_hive_ddl.hql  (DDL + MSCK + ANALYZE)
       └─ Step 3 Run_Queries_And_Metrics python3 run_queries.py
                                              ├─ for each query × {spark,hive}:
                                              │     spawn engine subprocess
                                              │     monitor peak RSS (psutil)
                                              │     parse YARN app id → fetch vcore/mem seconds
                                              │     append row to /tmp/query_metrics.csv
                                              └─ aws s3 cp metrics → S3
```

### Why Spark reads the same Hive tables

Spark is launched with `spark-sql`, which on EMR reads `hive-site.xml` and
connects to the Hive metastore, so it queries the **same external tables** as
Hive. This makes the comparison apples-to-apples (identical data + schema).
Spark still uses its own Catalyst optimizer, AQE, dynamic partition pruning and
vectorized Parquet reader — the shared catalog is metadata only and does not
slow Spark.

### Engine-specific tuning

- **Spark** (`spark/*.sql`): `BROADCAST()` hints for small dims, AQE, skew join,
  dynamic partition pruning, broadcast threshold 100 MB (set via `--conf`).
- **Hive** (`hive/*.hql`): Tez engine, vectorization, CBO, auto-convert-join
  with `MAPJOIN()` hints, parallel execution (set per file via `SET`).

## Resilience

- Per-query isolation: one failed query is recorded and the run continues.
- Metrics CSV is written incrementally after each query (survives a crash).
- The orchestrator uploads the metrics CSV to S3 before exiting.
- `action_on_failure = TERMINATE_CLUSTER` on every step → no orphan clusters.
- `INSERT OVERWRITE DIRECTORY` makes re-runs idempotent.

## The 9 queries

| # | Query | Tables | Metric |
|---|---|---|---|
| 1 | Top 20 clientes con mayor nº de compras | store_sales, customer | COUNT(DISTINCT ticket) |
| 2 | Ventas por tienda | store_sales, store | SUM(ext_sales_price) |
| 3 | Ventas por mes | store_sales, date_dim | SUM by d_year,d_moy |
| 4 | Ventas por día de la semana | store_sales, date_dim | SUM by d_dow,d_day_name |
| 5 | Top productos por tienda | store_sales, store, item | RANK() per store, top 10 |
| 6 | Ticket promedio por cliente | store_sales, customer | SUM(net_paid_inc_tax)/tickets |
| 7 | Productos con mayor ingreso | store_sales, item | SUM(ext_sales_price) top 20 |
| 8 | Top clientes por gasto total | store_sales, customer | SUM(net_paid_inc_tax) top 20 |
| 9 | Ranking mensual de ventas | store_sales, date_dim | RANK() over monthly totals |

Convention: "ventas/ingreso" = `ss_ext_sales_price`; "gasto/ticket" =
`ss_net_paid_inc_tax`; "compra" = distinct `ss_ticket_number`.
