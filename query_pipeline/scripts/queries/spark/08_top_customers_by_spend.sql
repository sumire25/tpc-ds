-- 08 - Top clientes por gasto total
-- Engine: Spark SQL
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/08_top_customers_by_spend'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT /*+ BROADCAST(c) */
    ss.ss_customer_sk   AS customer_sk,
    c.c_first_name      AS first_name,
    c.c_last_name       AS last_name,
    ROUND(SUM(ss.ss_net_paid_inc_tax), 2) AS total_spent
FROM store_sales ss
JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk
GROUP BY ss.ss_customer_sk, c.c_first_name, c.c_last_name
ORDER BY total_spent DESC
LIMIT 20;
