INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q8/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
SELECT c.c_first_name, c.c_last_name, sum(ss.ss_net_paid) as gasto_total 
FROM store_sales ss 
JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk 
GROUP BY c.c_first_name, c.c_last_name 
ORDER BY gasto_total DESC 
LIMIT 20;
