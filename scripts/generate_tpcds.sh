#!/bin/bash
set -euo pipefail

S3_BUCKET="onpe-datalake-mx"
S3_STAGING="s3://${S3_BUCKET}/staging/tpcds-10gb/"
DATA_DIR="/mnt/tpcds-data"
SCALE_FACTOR=10

echo "=== TPC-DS Data Generation Pipeline ==="
echo "Scale Factor: ${SCALE_FACTOR} (~${SCALE_FACTOR}GB)"
echo "Output: ${S3_STAGING}"
echo ""

sudo yum install -y gcc make flex bison byacc git

echo "[1/4] Cloning tpcds-kit repository..."
if [ -d "/tmp/tpcds-kit" ]; then
    rm -rf /tmp/tpcds-kit
fi
git clone https://github.com/gregrahn/tpcds-kit.git /tmp/tpcds-kit
cd /tmp/tpcds-kit/tools

echo "[2/4] Compiling tpcds-kit tools..."
make OS=LINUX

echo "[3/4] Generating TPC-DS data (scale=${SCALE_FACTOR})..."
mkdir -p "${DATA_DIR}"
./dsdgen -dir "${DATA_DIR}" -scale "${SCALE_FACTOR}" -force

echo "Generated files:"
ls -lh "${DATA_DIR}"/*.dat | awk '{print $5, $9}'

echo "[4/4] Uploading data to S3..."
aws s3 cp --recursive "${DATA_DIR}/" "${S3_STAGING}"

echo ""
echo "=== TPC-DS data generation complete ==="
echo "Data uploaded to: ${S3_STAGING}"
