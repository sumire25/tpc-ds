-- 06 - Ticket promedio por cliente
-- Engine: Spark SQL
-- Avg ticket = total paid (incl tax) / distinct tickets per customer
USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/spark/06_avg_ticket_by_customer'
USING CSV
OPTIONS ('header' = 'true', 'delimiter' = ',')
SELECT /*+ BROADCAST(c) */
    ss.ss_customer_sk   AS customer_sk,
    c.c_first_name      AS first_name,
    c.c_last_name       AS last_name,
    COUNT(DISTINCT ss.ss_ticket_number) AS tickets,
    ROUND(SUM(ss.ss_net_paid_inc_tax), 2) AS total_spent,
    ROUND(SUM(ss.ss_net_paid_inc_tax) / COUNT(DISTINCT ss.ss_ticket_number), 4) AS avg_ticket
FROM store_sales ss
JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk
GROUP BY ss.ss_customer_sk, c.c_first_name, c.c_last_name
ORDER BY avg_ticket DESC;
