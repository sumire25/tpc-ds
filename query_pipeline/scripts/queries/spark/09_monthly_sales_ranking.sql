-- 09 - Ranking mensual de ventas
-- Engine: Spark SQL
-- Monthly totals then rank across all months
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/09_monthly_sales_ranking'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT d_year, month, total_sales, sales_rank
FROM (
    SELECT
        d_year,
        month,
        total_sales,
        RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
    FROM (
        SELECT /*+ BROADCAST(d) */
            d.d_year,
            d.d_moy AS month,
            ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales
        FROM store_sales ss
        JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk
        GROUP BY d.d_year, d.d_moy
    ) monthly
) ranked
ORDER BY sales_rank;
