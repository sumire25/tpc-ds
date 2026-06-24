INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q6/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
SELECT c.c_first_name, c.c_last_name, 
       sum(ss.ss_net_paid) / count(distinct ss.ss_ticket_number) as ticket_promedio 
FROM store_sales ss 
JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk 
GROUP BY c.c_first_name, c.c_last_name
ORDER BY ticket_promedio DESC
LIMIT 20;
