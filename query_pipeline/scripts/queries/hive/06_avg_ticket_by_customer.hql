-- 06 - Ticket promedio por cliente
-- Engine: Hive on Tez
SET hive.execution.engine=tez;
SET hive.vectorized.execution.enabled=true;
SET hive.vectorized.execution.reduce.enabled=true;
SET hive.cbo.enable=true;
SET hive.compute.query.using.stats=true;
SET hive.stats.fetch.column.stats=true;
SET hive.auto.convert.join=true;
SET hive.auto.convert.join.noconditionaltask=true;
SET hive.auto.convert.join.noconditionaltask.size=104857600;
SET hive.exec.parallel=true;
SET hive.exec.parallel.thread.number=8;
SET tez.grouping.min-size=16777216;
SET tez.grouping.max-size=1073741824;

USE tpcds;

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/hive/06_avg_ticket_by_customer'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
SELECT /*+ MAPJOIN(c) */
    ss.ss_customer_sk,
    c.c_first_name,
    c.c_last_name,
    COUNT(DISTINCT ss.ss_ticket_number) AS tickets,
    ROUND(SUM(ss.ss_net_paid_inc_tax), 2) AS total_spent,
    ROUND(SUM(ss.ss_net_paid_inc_tax) / COUNT(DISTINCT ss.ss_ticket_number), 4) AS avg_ticket
FROM store_sales ss
JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk
GROUP BY ss.ss_customer_sk, c.c_first_name, c.c_last_name
ORDER BY avg_ticket DESC;
