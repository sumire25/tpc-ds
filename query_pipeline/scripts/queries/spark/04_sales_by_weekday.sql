-- 04 - Ventas por dia de la semana
-- Engine: Spark SQL
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/04_sales_by_weekday'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT /*+ BROADCAST(d) */
    d.d_dow      AS day_of_week,
    d.d_day_name AS day_name,
    ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales
FROM store_sales ss
JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk
GROUP BY d.d_dow, d.d_day_name
ORDER BY d.d_dow;
