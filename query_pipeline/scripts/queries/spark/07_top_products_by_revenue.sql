-- 07 - Productos con mayor ingreso generado
-- Engine: Spark SQL
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/07_top_products_by_revenue'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT /*+ BROADCAST(i) */
    ss.ss_item_sk    AS item_sk,
    i.i_product_name AS product_name,
    i.i_category     AS category,
    i.i_brand        AS brand,
    ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_revenue
FROM store_sales ss
JOIN item i ON ss.ss_item_sk = i.i_item_sk
GROUP BY ss.ss_item_sk, i.i_product_name, i.i_category, i.i_brand
ORDER BY total_revenue DESC
LIMIT 20;
