# AGENTS.md — query_pipeline

Guidance for opencode agents working in this folder.

## Layout

- `main.tf` — Terraform: uploads `scripts/**` to S3 and provisions the EMR
  cluster (Spark + Hive + Tez) with 3 sequential steps.
- `scripts/ddl/tpcds_hive_ddl.hql` — external Hive tables over the Parquet
  warehouse + `MSCK REPAIR` + `ANALYZE TABLE ... COMPUTE STATISTICS`.
- `scripts/queries/spark/*.sql` — Spark SQL queries (one INSERT OVERWRITE
  DIRECTORY per file). Each starts with `USE tpcds;`.
- `scripts/queries/hive/*.hql` — HiveQL queries (one per file). Each sets Tez /
  vectorization / CBO / auto-convert-join via `SET`, then `USE tpcds;`.
- `scripts/metrics/yarn_metrics.py` — peak-RSS monitor (`psutil`) + YARN REST
  client for `vcoreSeconds` / `memorySeconds`. Has a `psutil is None` fallback.
- `scripts/run_queries.py` — orchestrator. Discovers query files, runs each on
  both engines, writes `/tmp/query_metrics.csv` incrementally, uploads to S3.

## Conventions

- S3 bucket is hardcoded as `onpe-datalake-mx` (Learner Lab bucket).
- Engine tuning lives with the query files (SET / --conf), not only in TF.
- One query per file, named `NN_snake_case.{sql,hql}`.
- Output paths: `s3://onpe-datalake-mx/query_results/tpc-ds/{engine}/<query_name>/`.
- Metrics CSV: `s3://onpe-datalake-mx/query_results/tpc-ds/metrics/query_metrics.csv`.
- IAM reuses Learner Lab `LabRole` / `LabInstanceProfile` — do not redefine.
- No comments in code unless the file already uses header doc-comments.

## Verify before committing

Run from the repo root:

```bash
# Terraform formatting + validation (needs the AWS provider from .terraform)
terraform -chdir=query_pipeline fmt -check
terraform -chdir=query_pipeline validate

# Python syntax check
python3 -m py_compile query_pipeline/scripts/run_queries.py
python3 -m py_compile query_pipeline/scripts/metrics/yarn_metrics.py
```

There is no test suite and no live cluster in CI; correctness is verified by
static review + the metrics CSV after a real `terraform apply`.

## Adding a new query

1. Add `scripts/queries/spark/NN_name.sql` and `scripts/queries/hive/NN_name.hql`
   with the same `NN_name` so the orchestrator pairs them.
2. Spark: prefix with `USE tpcds;` and use
   `INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/NN_name' USING CSV OPTIONS (...)`.
3. Hive: prefix with the `SET` block + `USE tpcds;` and use
   `INSERT OVERWRITE DIRECTORY '...' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE`.
4. `terraform apply` re-uploads changed files (etag = filemd5) and the
   orchestrator picks them up automatically (it globs the directories).

## Do NOT

- Do not commit secrets or AWS credentials.
- Do not change the root `main.tf` from here; this module is independent.
- Do not enable `hive.limit.optimize.enable` — it samples and breaks top-N
  correctness.
