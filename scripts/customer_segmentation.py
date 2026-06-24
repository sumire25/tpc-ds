from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct, sum, max as spark_max, datediff, lit
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
import sys

def main():
    spark = SparkSession.builder.appName("Customer-Segmentation-ML") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

    S3_BUCKET = "onpe-datalake-mx"
    WAREHOUSE_PATH = f"s3://{S3_BUCKET}/warehouse/tpcds-10gb/"
    OUTPUT_PATH = f"s3://{S3_BUCKET}/warehouse/tpcds-10gb/customer_segments/"

    print("=== Starting Customer Segmentation ML Job ===")

    try:
        # 1. Load Data
        print("Loading Parquet data...")
        sales_df = spark.read.parquet(f"{WAREHOUSE_PATH}store_sales/")
        date_df = spark.read.parquet(f"{WAREHOUSE_PATH}date_dim/")
        customer_df = spark.read.parquet(f"{WAREHOUSE_PATH}customer/")
        
        # 2. Prepare Data for RFM (Recency, Frequency, Monetary)
        print("Calculating RFM metrics...")
        
        # Join sales with date to get actual dates
        sales_with_date = sales_df.join(
            date_df, 
            sales_df.ss_sold_date_sk == date_df.d_date_sk, 
            "inner"
        )

        # Find the maximum date in the dataset to act as 'today' for Recency calculation
        max_date_row = sales_with_date.agg(spark_max("d_date").alias("max_date")).collect()[0]
        current_date = max_date_row["max_date"]
        
        if not current_date:
            raise ValueError("Could not determine the maximum sales date. Data might be empty.")

        # Aggregate RFM by customer
        rfm_df = sales_with_date.groupBy("ss_customer_sk").agg(
            spark_max("d_date").alias("last_purchase_date"),
            countDistinct("ss_ticket_number").alias("frequency"),
            sum("ss_net_paid").alias("monetary")
        )

        # Calculate Recency in days
        rfm_df = rfm_df.withColumn(
            "recency", 
            datediff(lit(current_date), col("last_purchase_date"))
        ).na.fill({"monetary": 0.0})

        # 3. Feature Engineering for ML
        print("Assembling and scaling features...")
        assembler = VectorAssembler(
            inputCols=["recency", "frequency", "monetary"], 
            outputCol="features",
            handleInvalid="skip" # skip rows with nulls
        )
        assembled_df = assembler.transform(rfm_df)

        scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures", withStd=True, withMean=True)
        scaler_model = scaler.fit(assembled_df)
        scaled_df = scaler_model.transform(assembled_df)

        # 4. Train K-Means Model (k=5)
        print("Training K-Means clustering model (k=5)...")
        kmeans = KMeans(featuresCol="scaledFeatures", predictionCol="segment_id", k=5, seed=42)
        model = kmeans.fit(scaled_df)
        predictions = model.transform(scaled_df)

        # 5. Join back with customer details for a complete profile
        print("Joining segments with customer demographics...")
        final_segments = predictions.select("ss_customer_sk", "recency", "frequency", "monetary", "segment_id") \
            .join(customer_df, predictions.ss_customer_sk == customer_df.c_customer_sk, "inner") \
            .drop("ss_customer_sk") # drop duplicate key

        # 6. Save Results
        print(f"Writing customer segments to {OUTPUT_PATH}...")
        final_segments.write.mode("overwrite").parquet(OUTPUT_PATH)
        
        print("=== Customer Segmentation ML Job Completed Successfully ===")

    except Exception as e:
        print(f"CRITICAL ERROR: Spark job failed due to anomaly: {str(e)}")
        # We explicitly exit with a non-zero code to ensure EMR detects the failure and aborts/terminates.
        sys.exit(1)
        
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
