-- 02 - Ventas por tienda
-- Engine: Spark SQL
-- Metric: total sales (ss_ext_sales_price) per store
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/02_sales_by_store'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT /*+ BROADCAST(s) */
    ss.ss_store_sk   AS store_sk,
    s.s_store_name   AS store_name,
    s.s_city         AS city,
    s.s_state        AS state,
    COUNT(*)         AS transactions,
    ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales
FROM store_sales ss
JOIN store s ON ss.ss_store_sk = s.s_store_sk
GROUP BY ss.ss_store_sk, s.s_store_name, s.s_city, s.s_state
ORDER BY total_sales DESC;
