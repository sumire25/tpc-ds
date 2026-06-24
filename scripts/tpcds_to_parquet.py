from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, LongType, DoubleType, DecimalType
)

spark = SparkSession.builder.appName("TPC-DS-to-Parquet") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.sql.parquet.enableVectorizedReader", "true") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .config("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true") \
    .config("spark.sql.autoBroadcastJoinThreshold", "104857600") \
    .getOrCreate()

S3_BUCKET = "onpe-datalake-mx"
STAGING_PATH = f"s3://{S3_BUCKET}/staging/tpcds-10gb/"
OUTPUT_PATH = f"s3://{S3_BUCKET}/warehouse/tpcds-10gb/"

PIPE_DELIMITER = "|"

TABLES = {
    "date_dim": StructType([
        StructField("d_date_sk", IntegerType(), False),
        StructField("d_date_id", StringType(), False),
        StructField("d_date", StringType(), True),
        StructField("d_month_seq", IntegerType(), True),
        StructField("d_week_seq", IntegerType(), True),
        StructField("d_quarter_seq", IntegerType(), True),
        StructField("d_year", IntegerType(), True),
        StructField("d_dow", IntegerType(), True),
        StructField("d_moy", IntegerType(), True),
        StructField("d_dom", IntegerType(), True),
        StructField("d_qoy", IntegerType(), True),
        StructField("d_fy_year", IntegerType(), True),
        StructField("d_fy_quarter_seq", IntegerType(), True),
        StructField("d_fy_week_seq", IntegerType(), True),
        StructField("d_day_name", StringType(), True),
        StructField("d_quarter_name", StringType(), True),
        StructField("d_holiday", StringType(), True),
        StructField("d_weekend", StringType(), True),
        StructField("d_following_holiday", StringType(), True),
        StructField("d_first_dom", IntegerType(), True),
        StructField("d_last_dom", IntegerType(), True),
        StructField("d_same_day_ly", IntegerType(), True),
        StructField("d_same_day_lq", IntegerType(), True),
        StructField("d_current_day", StringType(), True),
        StructField("d_current_week", StringType(), True),
        StructField("d_current_month", StringType(), True),
        StructField("d_current_quarter", StringType(), True),
        StructField("d_current_year", StringType(), True),
    ]),

    "time_dim": StructType([
        StructField("t_time_sk", IntegerType(), False),
        StructField("t_time_id", StringType(), False),
        StructField("t_time", IntegerType(), True),
        StructField("t_hour", IntegerType(), True),
        StructField("t_minute", IntegerType(), True),
        StructField("t_second", IntegerType(), True),
        StructField("t_am_pm", StringType(), True),
        StructField("t_shift", StringType(), True),
        StructField("t_sub_shift", StringType(), True),
        StructField("t_meal_time", StringType(), True),
    ]),

    "item": StructType([
        StructField("i_item_sk", IntegerType(), False),
        StructField("i_item_id", StringType(), False),
        StructField("i_rec_start_date", StringType(), True),
        StructField("i_rec_end_date", StringType(), True),
        StructField("i_item_desc", StringType(), True),
        StructField("i_current_price", DoubleType(), True),
        StructField("i_wholesale_cost", DoubleType(), True),
        StructField("i_brand_id", IntegerType(), True),
        StructField("i_brand", StringType(), True),
        StructField("i_class_id", IntegerType(), True),
        StructField("i_class", StringType(), True),
        StructField("i_category_id", IntegerType(), True),
        StructField("i_category", StringType(), True),
        StructField("i_manufact_id", IntegerType(), True),
        StructField("i_manufact", StringType(), True),
        StructField("i_size", StringType(), True),
        StructField("i_formulation", StringType(), True),
        StructField("i_color", StringType(), True),
        StructField("i_units", StringType(), True),
        StructField("i_container", StringType(), True),
        StructField("i_manager_id", IntegerType(), True),
        StructField("i_product_name", StringType(), True),
    ]),

    "customer": StructType([
        StructField("c_customer_sk", IntegerType(), False),
        StructField("c_customer_id", StringType(), False),
        StructField("c_current_cdemo_sk", IntegerType(), True),
        StructField("c_current_hdemo_sk", IntegerType(), True),
        StructField("c_current_addr_sk", IntegerType(), True),
        StructField("c_first_shipto_date_sk", IntegerType(), True),
        StructField("c_first_sales_date_sk", IntegerType(), True),
        StructField("c_salutation", StringType(), True),
        StructField("c_first_name", StringType(), True),
        StructField("c_last_name", StringType(), True),
        StructField("c_preferred_cust_flag", StringType(), True),
        StructField("c_birth_day", IntegerType(), True),
        StructField("c_birth_month", IntegerType(), True),
        StructField("c_birth_year", IntegerType(), True),
        StructField("c_birth_country", StringType(), True),
        StructField("c_login", StringType(), True),
        StructField("c_email_address", StringType(), True),
        StructField("c_last_review_date", StringType(), True),
        StructField("c_last_review_date_sk", IntegerType(), True),
    ]),

    "customer_address": StructType([
        StructField("ca_address_sk", IntegerType(), False),
        StructField("ca_address_id", StringType(), False),
        StructField("ca_street_number", StringType(), True),
        StructField("ca_street_name", StringType(), True),
        StructField("ca_street_type", StringType(), True),
        StructField("ca_suite_number", StringType(), True),
        StructField("ca_city", StringType(), True),
        StructField("ca_county", StringType(), True),
        StructField("ca_state", StringType(), True),
        StructField("ca_zip", StringType(), True),
        StructField("ca_country", StringType(), True),
        StructField("ca_gmt_offset", DoubleType(), True),
        StructField("ca_location_type", StringType(), True),
    ]),

    "customer_demographics": StructType([
        StructField("cd_demo_sk", IntegerType(), False),
        StructField("cd_gender", StringType(), True),
        StructField("cd_marital_status", StringType(), True),
        StructField("cd_education_status", StringType(), True),
        StructField("cd_purchase_estimate", IntegerType(), True),
        StructField("cd_credit_rating", StringType(), True),
        StructField("cd_dep_count", IntegerType(), True),
        StructField("cd_dep_employed_count", IntegerType(), True),
        StructField("cd_dep_college_count", IntegerType(), True),
    ]),

    "store": StructType([
        StructField("s_store_sk", IntegerType(), False),
        StructField("s_store_id", StringType(), False),
        StructField("s_rec_start_date", StringType(), True),
        StructField("s_rec_end_date", StringType(), True),
        StructField("s_closed_date_sk", IntegerType(), True),
        StructField("s_store_name", StringType(), True),
        StructField("s_number_employees", IntegerType(), True),
        StructField("s_floor_space", IntegerType(), True),
        StructField("s_hours", StringType(), True),
        StructField("s_manager", StringType(), True),
        StructField("s_market_id", IntegerType(), True),
        StructField("s_geography_class", StringType(), True),
        StructField("s_market_desc", StringType(), True),
        StructField("s_market_manager", StringType(), True),
        StructField("s_division_id", IntegerType(), True),
        StructField("s_division_name", StringType(), True),
        StructField("s_company_id", IntegerType(), True),
        StructField("s_company_name", StringType(), True),
        StructField("s_street_number", StringType(), True),
        StructField("s_street_name", StringType(), True),
        StructField("s_street_type", StringType(), True),
        StructField("s_suite_number", StringType(), True),
        StructField("s_city", StringType(), True),
        StructField("s_county", StringType(), True),
        StructField("s_state", StringType(), True),
        StructField("s_zip", StringType(), True),
        StructField("s_country", StringType(), True),
        StructField("s_gmt_offset", DoubleType(), True),
        StructField("s_tax_precentage", DoubleType(), True),
    ]),

    "store_sales": StructType([
        StructField("ss_sold_date_sk", IntegerType(), True),
        StructField("ss_sold_time_sk", IntegerType(), True),
        StructField("ss_item_sk", IntegerType(), False),
        StructField("ss_customer_sk", IntegerType(), True),
        StructField("ss_cdemo_sk", IntegerType(), True),
        StructField("ss_hdemo_sk", IntegerType(), True),
        StructField("ss_addr_sk", IntegerType(), True),
        StructField("ss_store_sk", IntegerType(), True),
        StructField("ss_promo_sk", IntegerType(), True),
        StructField("ss_ticket_number", IntegerType(), False),
        StructField("ss_quantity", IntegerType(), True),
        StructField("ss_wholesale_cost", DoubleType(), True),
        StructField("ss_list_price", DoubleType(), True),
        StructField("ss_sales_price", DoubleType(), True),
        StructField("ss_ext_discount_amt", DoubleType(), True),
        StructField("ss_ext_sales_price", DoubleType(), True),
        StructField("ss_ext_wholesale_cost", DoubleType(), True),
        StructField("ss_ext_list_price", DoubleType(), True),
        StructField("ss_ext_tax", DoubleType(), True),
        StructField("ss_coupon_amt", DoubleType(), True),
        StructField("ss_net_paid", DoubleType(), True),
        StructField("ss_net_paid_inc_tax", DoubleType(), True),
        StructField("ss_net_profit", DoubleType(), True),
    ]),

    "store_returns": StructType([
        StructField("sr_returned_date_sk", IntegerType(), True),
        StructField("sr_return_time_sk", IntegerType(), True),
        StructField("sr_item_sk", IntegerType(), False),
        StructField("sr_customer_sk", IntegerType(), True),
        StructField("sr_cdemo_sk", IntegerType(), True),
        StructField("sr_hdemo_sk", IntegerType(), True),
        StructField("sr_addr_sk", IntegerType(), True),
        StructField("sr_store_sk", IntegerType(), True),
        StructField("sr_reason_sk", IntegerType(), True),
        StructField("sr_ticket_number", IntegerType(), False),
        StructField("sr_return_quantity", IntegerType(), True),
        StructField("sr_return_amt", DoubleType(), True),
        StructField("sr_return_tax", DoubleType(), True),
        StructField("sr_return_amt_inc_tax", DoubleType(), True),
        StructField("sr_fee", DoubleType(), True),
        StructField("sr_return_ship_cost", DoubleType(), True),
        StructField("sr_refunded_cash", DoubleType(), True),
        StructField("sr_reversed_charge", DoubleType(), True),
        StructField("sr_store_credit", DoubleType(), True),
        StructField("sr_net_loss", DoubleType(), True),
    ]),

    "catalog_sales": StructType([
        StructField("cs_sold_date_sk", IntegerType(), True),
        StructField("cs_sold_time_sk", IntegerType(), True),
        StructField("cs_ship_date_sk", IntegerType(), True),
        StructField("cs_bill_customer_sk", IntegerType(), True),
        StructField("cs_bill_cdemo_sk", IntegerType(), True),
        StructField("cs_bill_hdemo_sk", IntegerType(), True),
        StructField("cs_bill_addr_sk", IntegerType(), True),
        StructField("cs_ship_customer_sk", IntegerType(), True),
        StructField("cs_ship_cdemo_sk", IntegerType(), True),
        StructField("cs_ship_hdemo_sk", IntegerType(), True),
        StructField("cs_ship_addr_sk", IntegerType(), True),
        StructField("cs_call_center_sk", IntegerType(), True),
        StructField("cs_catalog_page_sk", IntegerType(), True),
        StructField("cs_ship_mode_sk", IntegerType(), True),
        StructField("cs_warehouse_sk", IntegerType(), True),
        StructField("cs_item_sk", IntegerType(), False),
        StructField("cs_promo_sk", IntegerType(), True),
        StructField("cs_order_number", IntegerType(), False),
        StructField("cs_quantity", IntegerType(), True),
        StructField("cs_wholesale_cost", DoubleType(), True),
        StructField("cs_list_price", DoubleType(), True),
        StructField("cs_sales_price", DoubleType(), True),
        StructField("cs_ext_discount_amt", DoubleType(), True),
        StructField("cs_ext_sales_price", DoubleType(), True),
        StructField("cs_ext_wholesale_cost", DoubleType(), True),
        StructField("cs_ext_list_price", DoubleType(), True),
        StructField("cs_ext_tax", DoubleType(), True),
        StructField("cs_coupon_amt", DoubleType(), True),
        StructField("cs_ext_ship_cost", DoubleType(), True),
        StructField("cs_net_paid", DoubleType(), True),
        StructField("cs_net_paid_inc_tax", DoubleType(), True),
        StructField("cs_net_paid_inc_ship", DoubleType(), True),
        StructField("cs_net_paid_inc_ship_tax", DoubleType(), True),
        StructField("cs_net_profit", DoubleType(), True),
    ]),

    "web_sales": StructType([
        StructField("ws_sold_date_sk", IntegerType(), True),
        StructField("ws_sold_time_sk", IntegerType(), True),
        StructField("ws_ship_date_sk", IntegerType(), True),
        StructField("ws_item_sk", IntegerType(), False),
        StructField("ws_bill_customer_sk", IntegerType(), True),
        StructField("ws_bill_cdemo_sk", IntegerType(), True),
        StructField("ws_bill_hdemo_sk", IntegerType(), True),
        StructField("ws_bill_addr_sk", IntegerType(), True),
        StructField("ws_ship_customer_sk", IntegerType(), True),
        StructField("ws_ship_cdemo_sk", IntegerType(), True),
        StructField("ws_ship_hdemo_sk", IntegerType(), True),
        StructField("ws_ship_addr_sk", IntegerType(), True),
        StructField("ws_web_page_sk", IntegerType(), True),
        StructField("ws_web_site_sk", IntegerType(), True),
        StructField("ws_ship_mode_sk", IntegerType(), True),
        StructField("ws_warehouse_sk", IntegerType(), True),
        StructField("ws_promo_sk", IntegerType(), True),
        StructField("ws_order_number", IntegerType(), False),
        StructField("ws_quantity", IntegerType(), True),
        StructField("ws_wholesale_cost", DoubleType(), True),
        StructField("ws_list_price", DoubleType(), True),
        StructField("ws_sales_price", DoubleType(), True),
        StructField("ws_ext_discount_amt", DoubleType(), True),
        StructField("ws_ext_sales_price", DoubleType(), True),
        StructField("ws_ext_wholesale_cost", DoubleType(), True),
        StructField("ws_ext_list_price", DoubleType(), True),
        StructField("ws_ext_tax", DoubleType(), True),
        StructField("ws_coupon_amt", DoubleType(), True),
        StructField("ws_ext_ship_cost", DoubleType(), True),
        StructField("ws_net_paid", DoubleType(), True),
        StructField("ws_net_paid_inc_tax", DoubleType(), True),
        StructField("ws_net_paid_inc_ship", DoubleType(), True),
        StructField("ws_net_paid_inc_ship_tax", DoubleType(), True),
        StructField("ws_net_profit", DoubleType(), True),
    ]),

    "promotion": StructType([
        StructField("p_promo_sk", IntegerType(), False),
        StructField("p_promo_id", StringType(), False),
        StructField("p_start_date_sk", IntegerType(), True),
        StructField("p_end_date_sk", IntegerType(), True),
        StructField("p_item_sk", IntegerType(), True),
        StructField("p_cost", DoubleType(), True),
        StructField("p_response_target", IntegerType(), True),
        StructField("p_promo_name", StringType(), True),
        StructField("p_channel_dmail", StringType(), True),
        StructField("p_channel_email", StringType(), True),
        StructField("p_channel_catalog", StringType(), True),
        StructField("p_channel_tv", StringType(), True),
        StructField("p_channel_radio", StringType(), True),
        StructField("p_channel_press", StringType(), True),
        StructField("p_channel_event", StringType(), True),
        StructField("p_channel_demo", StringType(), True),
        StructField("p_channel_details", StringType(), True),
        StructField("p_purpose", StringType(), True),
        StructField("p_discount_active", StringType(), True),
    ]),

    "household_demographics": StructType([
        StructField("hd_demo_sk", IntegerType(), False),
        StructField("hd_income_band_sk", IntegerType(), True),
        StructField("hd_buy_potential", StringType(), True),
        StructField("hd_dep_count", IntegerType(), True),
        StructField("hd_vehicle_count", IntegerType(), True),
    ]),

    "income_band": StructType([
        StructField("ib_income_band_sk", IntegerType(), False),
        StructField("ib_lower_bound", IntegerType(), True),
        StructField("ib_upper_bound", IntegerType(), True),
    ]),
}

for table_name, schema in TABLES.items():
    print(f"Processing table: {table_name}")
    input_path = f"{STAGING_PATH}{table_name}.dat"

    try:
        df = spark.read \
            .option("delimiter", PIPE_DELIMITER) \
            .option("header", "false") \
            .option("mode", "PERMISSIVE") \
            .schema(schema) \
            .csv(input_path)

        row_count = df.count()
        print(f"  Read {row_count} rows from {input_path}")

        output_table_path = f"{OUTPUT_PATH}{table_name}/"
        
        # Partition large fact tables by date surrogate key
        partition_col = None
        if table_name == "store_sales":
            partition_col = "ss_sold_date_sk"
        elif table_name == "store_returns":
            partition_col = "sr_returned_date_sk"
        elif table_name == "catalog_sales":
            partition_col = "cs_sold_date_sk"
        elif table_name == "web_sales":
            partition_col = "ws_sold_date_sk"

        writer = df.write.mode("overwrite")
        if partition_col:
            writer = writer.partitionBy(partition_col)
            
        writer.parquet(output_table_path)

        print(f"  Written Parquet to {output_table_path}")

    except Exception as e:
        print(f"  ERROR processing {table_name}: {e}")

print("")
print("=== TPC-DS to Parquet conversion complete ===")
print(f"Parquet files available at: {OUTPUT_PATH}")

spark.stop()
