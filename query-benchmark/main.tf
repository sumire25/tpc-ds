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
  type    = string
  default = "onpe-datalake-mx"
}

# --- Script Uploads ---

resource "aws_s3_object" "run_benchmark" {
  bucket = var.my_datalake_bucket
  key    = "artifacts/benchmark_scripts/run_benchmark.sh"
  source = "${path.module}/scripts/run_benchmark.sh"
  etag   = filemd5("${path.module}/scripts/run_benchmark.sh")
}

resource "aws_s3_object" "spark_query_runner" {
  bucket = var.my_datalake_bucket
  key    = "artifacts/benchmark_scripts/spark_query_runner.py"
  source = "${path.module}/scripts/spark_query_runner.py"
  etag   = filemd5("${path.module}/scripts/spark_query_runner.py")
}

resource "aws_s3_object" "fetch_yarn_metrics" {
  bucket = var.my_datalake_bucket
  key    = "artifacts/benchmark_scripts/fetch_yarn_metrics.py"
  source = "${path.module}/scripts/fetch_yarn_metrics.py"
  etag   = filemd5("${path.module}/scripts/fetch_yarn_metrics.py")
}

resource "aws_s3_object" "hive_setup" {
  bucket = var.my_datalake_bucket
  key    = "artifacts/benchmark_scripts/hive_setup.hql"
  source = "${path.module}/scripts/hive_setup.hql"
  etag   = filemd5("${path.module}/scripts/hive_setup.hql")
}

resource "aws_s3_object" "hive_queries" {
  count  = 9
  bucket = var.my_datalake_bucket
  key    = "artifacts/benchmark_scripts/hive_queries/q${count.index + 1}.hql"
  source = "${path.module}/scripts/hive_queries/q${count.index + 1}.hql"
  etag   = filemd5("${path.module}/scripts/hive_queries/q${count.index + 1}.hql")
}

# --- EMR Cluster ---
resource "aws_emr_cluster" "benchmark_cluster" {
  name          = "TPC-DS-Query-Benchmark"
  release_label = "emr-6.15.0"
  applications  = ["Hadoop", "Spark", "Hive"]

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

  # Download and Run Benchmark Script
  step {
    name              = "Download_and_Run_Benchmark"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "s3://us-east-1.elasticmapreduce/libs/script-runner/script-runner.jar"
      args = [
        "s3://${var.my_datalake_bucket}/artifacts/benchmark_scripts/run_benchmark.sh"
      ]
    }
  }

  keep_job_flow_alive_when_no_steps = false

  depends_on = [
    aws_s3_object.run_benchmark,
    aws_s3_object.spark_query_runner,
    aws_s3_object.fetch_yarn_metrics,
    aws_s3_object.hive_setup,
    aws_s3_object.hive_queries
  ]
}
