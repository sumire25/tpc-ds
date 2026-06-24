#!/bin/bash

# Configuration
S3_BUCKET="onpe-datalake-mx"
RESULTS_S3="s3://${S3_BUCKET}/query_results/tpc-ds"
SCRIPTS_S3="s3://${S3_BUCKET}/artifacts/benchmark_scripts"
METRICS_DIR="/tmp/metrics"

echo "=== Starting TPC-DS Spark vs Hive Benchmark ==="
echo "Metrics output will be stored in: ${METRICS_DIR}"

# Clear old metrics
rm -rf ${METRICS_DIR}
mkdir -p ${METRICS_DIR}

# Step 1: Download all scripts from S3
echo "Downloading scripts..."
aws s3 cp ${SCRIPTS_S3}/hive_setup.hql /tmp/hive_setup.hql
aws s3 cp ${SCRIPTS_S3}/spark_query_runner.py /tmp/spark_query_runner.py
aws s3 cp ${SCRIPTS_S3}/fetch_yarn_metrics.py /tmp/fetch_yarn_metrics.py
mkdir -p /tmp/hive_queries
for i in {1..9}; do
    aws s3 cp ${SCRIPTS_S3}/hive_queries/q${i}.hql /tmp/hive_queries/q${i}.hql
done

# Step 2: Run Hive Setup
echo "Running Hive Setup (Creating EXTERNAL Parquet tables)..."
hive -f /tmp/hive_setup.hql
if [ $? -ne 0 ]; then
    echo "ERROR: Hive setup failed!"
    exit 1
fi

# Step 3: Run Queries 1 to 9 sequentially for both Spark and Hive
for i in {1..9}; do
    echo "=========================================="
    echo "          Running Query ${i}"
    echo "=========================================="
    
    # SPARK EXECUTION
    echo ">>> Running SPARK Query ${i}..."
    SPARK_METRICS="${METRICS_DIR}/q${i}_spark_metrics.txt"
    echo -e "=== SPARK QUERY ${i} METRICS ===" > ${SPARK_METRICS}
    
    /usr/bin/time -v spark-submit \
        --deploy-mode cluster \
        --master yarn \
        --executor-memory 4g \
        --num-executors 4 \
        /tmp/spark_query_runner.py --query ${i} \
        2>> ${SPARK_METRICS}
        
    if [ $? -ne 0 ]; then
        echo "ERROR: Spark Query ${i} failed!"
    fi
    
    # Auto-fetch YARN metrics for Spark Job
    python3 /tmp/fetch_yarn_metrics.py ${SPARK_METRICS}
    
    # HIVE EXECUTION
    echo ">>> Running HIVE Query ${i}..."
    HIVE_METRICS="${METRICS_DIR}/q${i}_hive_metrics.txt"
    echo -e "=== HIVE QUERY ${i} METRICS ===" > ${HIVE_METRICS}
    
    /usr/bin/time -v hive -f /tmp/hive_queries/q${i}.hql \
        2>> ${HIVE_METRICS}
        
    if [ $? -ne 0 ]; then
        echo "ERROR: Hive Query ${i} failed!"
    fi
    
    # Auto-fetch YARN metrics for Hive Job
    python3 /tmp/fetch_yarn_metrics.py ${HIVE_METRICS}
done

# Step 4: Upload Metrics to S3
echo "Uploading metrics to S3..."
aws s3 cp ${METRICS_DIR}/ ${RESULTS_S3}/metrics/ --recursive

echo "=== Benchmark Complete ==="
