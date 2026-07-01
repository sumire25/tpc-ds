-- 05 - Top productos por tienda (top 10 per store)
-- Engine: Spark SQL
-- Window rank partitioned by store; broadcast store + item dims
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/05_top_products_by_store'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT store_sk, store_name, item_sk, product_name, category, total_sales, rk AS rank
FROM (
    SELECT /*+ BROADCAST(s), BROADCAST(i) */
        ss.ss_store_sk          AS store_sk,
        s.s_store_name          AS store_name,
        ss.ss_item_sk           AS item_sk,
        i.i_product_name        AS product_name,
        i.i_category            AS category,
        ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales,
        RANK() OVER (PARTITION BY ss.ss_store_sk ORDER BY SUM(ss.ss_ext_sales_price) DESC) AS rk
    FROM store_sales ss
    JOIN store s ON ss.ss_store_sk = s.s_store_sk
    JOIN item  i ON ss.ss_item_sk  = i.i_item_sk
    GROUP BY ss.ss_store_sk, s.s_store_name, ss.ss_item_sk, i.i_product_name, i.i_category
) t
WHERE rk <= 10
ORDER BY store_sk, rank;
