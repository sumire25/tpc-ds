-- 01 - Top 20 clientes con mayor numero de compras
-- Engine: Spark SQL (enableHiveSupport over tpcds.* catalog)
-- Metric: number of distinct purchase tickets (ss_ticket_number) per customer
-- Optimizations: broadcast small customer dim; DPP not needed (no date filter)
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/01_top_customers_by_purchases'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT /*+ BROADCAST(c) */
    ss.ss_customer_sk      AS customer_sk,
    c.c_first_name         AS first_name,
    c.c_last_name          AS last_name,
    COUNT(DISTINCT ss.ss_ticket_number) AS purchases_count,
    ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales
FROM store_sales ss
JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk
GROUP BY ss.ss_customer_sk, c.c_first_name, c.c_last_name
ORDER BY purchases_count DESC, total_sales DESC
LIMIT 20;
