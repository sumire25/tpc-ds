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

resource "aws_s3_object" "generate_script" {
  bucket = var.my_datalake_bucket
  key    = "artifacts/tpcds/generate_tpcds.sh"
  source = "${path.module}/scripts/generate_tpcds.sh"
  etag   = filemd5("${path.module}/scripts/generate_tpcds.sh")
}

resource "aws_s3_object" "parquet_script" {
  bucket = var.my_datalake_bucket
  key    = "artifacts/tpcds/tpcds_to_parquet.py"
  source = "${path.module}/scripts/tpcds_to_parquet.py"
  etag   = filemd5("${path.module}/scripts/tpcds_to_parquet.py")
}

resource "aws_s3_object" "ml_script" {
  bucket = var.my_datalake_bucket
  key    = "artifacts/tpcds/customer_segmentation.py"
  source = "${path.module}/scripts/customer_segmentation.py"
  etag   = filemd5("${path.module}/scripts/customer_segmentation.py")
}

resource "aws_emr_cluster" "tpcds_pipeline" {
  name          = "TPC-DS-DataGeneration-Parquet"
  release_label = "emr-6.15.0"
  applications  = ["Hadoop", "Spark"]

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

  tags = {
    Name        = "TPC-DS-DataGeneration-Parquet"
    Environment = "lab"
    Project     = "big-data-tpcds"
  }

  step {
    name              = "Generate_TPC-DS_10GB"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "bash",
        "-c",
        "aws s3 cp s3://${var.my_datalake_bucket}/artifacts/tpcds/generate_tpcds.sh /tmp/generate_tpcds.sh && chmod +x /tmp/generate_tpcds.sh && /tmp/generate_tpcds.sh"
      ]
    }
  }

  step {
    name              = "Convert_TPC-DS_to_Parquet"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "spark-submit",
        "--deploy-mode", "cluster",
        "--master", "yarn",
        "--executor-memory", "4g",
        "--num-executors", "4",
        "s3://${var.my_datalake_bucket}/artifacts/tpcds/tpcds_to_parquet.py"
      ]
    }
  }

  step {
    name              = "Customer_Segmentation_ML"
    action_on_failure = "TERMINATE_CLUSTER"

    hadoop_jar_step {
      jar = "command-runner.jar"
      args = [
        "spark-submit",
        "--deploy-mode", "cluster",
        "--master", "yarn",
        "--executor-memory", "4g",
        "--num-executors", "4",
        "s3://${var.my_datalake_bucket}/artifacts/tpcds/customer_segmentation.py"
      ]
    }
  }

  keep_job_flow_alive_when_no_steps = false

  depends_on = [aws_s3_object.generate_script, aws_s3_object.parquet_script, aws_s3_object.ml_script]
}
