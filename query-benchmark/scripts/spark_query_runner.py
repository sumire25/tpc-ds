import argparse
import sys
from pyspark.sql import SparkSession

def get_query(query_id):
    queries = {
        1: """
            SELECT c.c_first_name, c.c_last_name, count(ss.ss_ticket_number) as num_compras 
            FROM store_sales ss 
            JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk 
            GROUP BY c.c_first_name, c.c_last_name 
            ORDER BY num_compras DESC 
            LIMIT 20
        """,
        2: """
            SELECT s.s_store_name, sum(ss.ss_net_paid) as total_ventas 
            FROM store_sales ss 
            JOIN store s ON ss.ss_store_sk = s.s_store_sk 
            GROUP BY s.s_store_name
            ORDER BY total_ventas DESC
        """,
        3: """
            SELECT d.d_year, d.d_moy, sum(ss.ss_net_paid) as total_ventas 
            FROM store_sales ss 
            JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk 
            GROUP BY d.d_year, d.d_moy 
            ORDER BY d.d_year, d.d_moy
        """,
        4: """
            SELECT d.d_day_name, sum(ss.ss_net_paid) as total_ventas 
            FROM store_sales ss 
            JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk 
            GROUP BY d.d_day_name
            ORDER BY total_ventas DESC
        """,
        5: """
            WITH ranked_products AS (
                SELECT s.s_store_name, i.i_product_name, sum(ss.ss_net_paid) as total_ventas,
                       ROW_NUMBER() OVER (PARTITION BY s.s_store_name ORDER BY sum(ss.ss_net_paid) DESC) as rnk
                FROM store_sales ss 
                JOIN store s ON ss.ss_store_sk = s.s_store_sk 
                JOIN item i ON ss.ss_item_sk = i.i_item_sk
                GROUP BY s.s_store_name, i.i_product_name
            )
            SELECT s_store_name, i_product_name, total_ventas 
            FROM ranked_products 
            WHERE rnk = 1
        """,
        6: """
            SELECT c.c_first_name, c.c_last_name, 
                   sum(ss.ss_net_paid) / count(distinct ss.ss_ticket_number) as ticket_promedio 
            FROM store_sales ss 
            JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk 
            GROUP BY c.c_first_name, c.c_last_name
            ORDER BY ticket_promedio DESC
            LIMIT 20
        """,
        7: """
            SELECT i.i_product_name, sum(ss.ss_net_paid) as ingresos 
            FROM store_sales ss 
            JOIN item i ON ss.ss_item_sk = i.i_item_sk 
            GROUP BY i.i_product_name 
            ORDER BY ingresos DESC 
            LIMIT 20
        """,
        8: """
            SELECT c.c_first_name, c.c_last_name, sum(ss.ss_net_paid) as gasto_total 
            FROM store_sales ss 
            JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk 
            GROUP BY c.c_first_name, c.c_last_name 
            ORDER BY gasto_total DESC 
            LIMIT 20
        """,
        9: """
            SELECT d.d_year, d.d_moy, sum(ss.ss_net_paid) as total_ventas,
                   RANK() OVER (PARTITION BY d.d_year ORDER BY sum(ss.ss_net_paid) DESC) as ranking_mensual
            FROM store_sales ss 
            JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk 
            GROUP BY d.d_year, d.d_moy
            ORDER BY d.d_year, ranking_mensual
        """
    }
    return queries.get(query_id)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=int, required=True, help="Query number to execute (1-9)")
    args = parser.parse_args()
    
    query_id = args.query
    query_sql = get_query(query_id)
    if not query_sql:
        print(f"Invalid query ID: {query_id}")
        sys.exit(1)

    spark = SparkSession.builder.appName(f"Spark-Benchmark-Q{query_id}") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

    S3_BUCKET = "onpe-datalake-mx"
    WAREHOUSE_PATH = f"s3://{S3_BUCKET}/warehouse/tpcds-10gb/"
    OUTPUT_PATH = f"s3://{S3_BUCKET}/query_results/tpc-ds/spark/q{query_id}/"

    print(f"=== Starting Spark Benchmark Query {query_id} ===")

    try:
        # Load tables as temporary views
        spark.read.parquet(f"{WAREHOUSE_PATH}store_sales/").createOrReplaceTempView("store_sales")
        spark.read.parquet(f"{WAREHOUSE_PATH}customer/").createOrReplaceTempView("customer")
        spark.read.parquet(f"{WAREHOUSE_PATH}store/").createOrReplaceTempView("store")
        spark.read.parquet(f"{WAREHOUSE_PATH}date_dim/").createOrReplaceTempView("date_dim")
        spark.read.parquet(f"{WAREHOUSE_PATH}item/").createOrReplaceTempView("item")
        
        print("Executing query...")
        result_df = spark.sql(query_sql)

        print(f"Writing results to {OUTPUT_PATH}...")
        result_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(OUTPUT_PATH)
        
        print(f"=== Query {query_id} Completed Successfully ===")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)
        
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
