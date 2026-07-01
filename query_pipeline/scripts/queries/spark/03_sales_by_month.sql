-- 03 - Ventas por mes
-- Engine: Spark SQL
-- Joins date_dim so dynamic partition pruning prunes store_sales partitions
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/03_sales_by_month'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT /*+ BROADCAST(d) */
    d.d_year,
    d.d_moy  AS month,
    ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales
FROM store_sales ss
JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk
GROUP BY d.d_year, d.d_moy
ORDER BY d.d_year, d.d_moy;
