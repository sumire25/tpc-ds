# =============================================================================
# TPC-DS Query & Metrics Pipeline
# Provisions a dedicated EMR cluster (Hadoop + Spark + Hive + Tez) that:
#   1. Copies scripts to the master node
#   2. Creates Hive external tables (only tables used by queries)
#   3. Runs the 9 Hive queries, capturing per-query metrics
#   4. Runs the 9 Spark queries, capturing per-query metrics
#   5. Auto-terminates on completion (or on step failure, for cost safety)
#
# This is independent from the root main.tf (data generation) which already ran.
# Apply from this folder:  terraform init && terraform apply
# =============================================================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "my_datalake_bucket" {
  type        = string
  description = "The S3 bucket name for the Learner Lab"
  default     = "onpe-datalake-mx"
}

locals {
  scripts_dir  = "${path.module}/scripts"
  artifact_key = "artifacts/tpcds_queries/scripts"
  # Upload every script file, excluding Python bytecode caches so they never
  # leak into S3 artifacts. (Map form so for_each keys are the relative paths.)
  script_files = {
    for f in fileset(local.scripts_dir, "**") : f => f
    if !strcontains(f, "__pycache__")
  }
}

# -----------------------------------------------------------------------------
# Upload all pipeline scripts to S3 (idempotent via etag = filemd5)
# -----------------------------------------------------------------------------
resource "aws_s3_object" "query_scripts" {
  for_each = local.script_files
  bucket   = var.my_datalake_bucket
  key      = "${local.artifact_key}/${each.key}"
  source   = "${local.scripts_dir}/${each.key}"
  etag     = filemd5("${local.scripts_dir}/${each.key}")
}

# -----------------------------------------------------------------------------
# EMR cluster: Spark + Hive + Tez
# -----------------------------------------------------------------------------
resource "aws_emr_cluster" "tpcds_queries" {
  name          = "TPC-DS-Queries-SparkVsHive"
  release_label = "emr-6.15.0"
  applications  = ["Hadoop", "Spark", "Hive", "Tez"]

  service_role = "LabRole"

  ec2_attributes {
    instance_profile = "LabInstanceProfile"
  }

  master_instance_group {
    instance_type  = "m4.large"
    instance_count = 1
  }

  core_instance_group {
    instance_type  = "m4.large"
    instance_count = 4
  }

  log_uri = "s3://${var.my_datalake_bucket}/emr-logs/"

  # Cluster-wide engine defaults (per-query SET / --conf still apply on top)
  configurations_json = jsonencode([
    {
      classification = "hive-site"
      properties = {
        "hive.execution.engine"                         = "tez"
        "hive.vectorized.execution.enabled"             = "true"
        "hive.vectorized.execution.reduce.enabled"      = "true"
        "hive.cbo.enable"                               = "true"
        "hive.compute.query.using.stats"                = "true"
        "hive.stats.fetch.column.stats"                 = "true"
        "hive.auto.convert.join"                        = "true"
        "hive.auto.convert.join.noconditionaltask"      = "true"
        "hive.auto.convert.join.noconditionaltask.size" = "104857600"
        "hive.exec.parallel"                            = "true"
        "hive.exec.parallel.thread.number"              = "8"
      }
    },
    {
      classification = "spark-defaults"
      properties = {
        "spark.sql.adaptive.enabled"                          = "true"
        "spark.sql.adaptive.coalescePartitions.enabled"       = "true"
        "spark.sql.adaptive.skewJoin.enabled"                 = "true"
        "spark.sql.optimizer.dynamicPartitionPruning.enabled" = "true"
        "spark.sql.autoBroadcastJoinThreshold"                = "104857600"
        "spark.sql.parquet.filterPushdown"                    = "true"
        "spark.sql.parquet.enableVectorizedReader"            = "true"
      }
    },
    {
      classification = "tez-site"
      properties = {
        "tez.grouping.min-size" = "16777216"
        "tez.grouping.max-size" = "1073741824"
      }
    }
  ])

  tags = {
    Name        = "TPC-DS-Queries-SparkVsHive"
    Environment = "lab"
    Project     = "big-data-tpcds"
    Phase       = "queries"
  }

  # ---- Step 1: copy scripts locally + install psutil for the metrics monitor ----
  step {
    name              = "Stage_Scripts"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "bash",
        "-c",
        "aws s3 cp --recursive s3://${var.my_datalake_bucket}/${local.artifact_key}/ /tmp/tpcds_queries/scripts/ && pip3 install --quiet psutil || true"
      ]
    }
  }

  # ---- Step 2: create Hive external tables + repair partitions ----
  step {
    name              = "Create_Hive_Tables"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "hive",
        "-f",
        "/tmp/tpcds_queries/scripts/ddl/tpcds_hive_ddl.hql"
      ]
    }
  }

  # ---- Step 3: run Hive queries and collect metrics ----
  step {
    name              = "Run_Hive_Queries"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "bash",
        "-c",
        "cd /tmp/tpcds_queries/scripts && python3 run_hive_queries.py"
      ]
    }
  }

  # ---- Step 4: run Spark queries and collect metrics ----
  step {
    name              = "Run_Spark_Queries"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "bash",
        "-c",
        "cd /tmp/tpcds_queries/scripts && python3 run_spark_queries.py"
      ]
    }
  }

  keep_job_flow_alive_when_no_steps = false

  depends_on = [aws_s3_object.query_scripts]
}
