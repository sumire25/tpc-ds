INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q1/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
SELECT c.c_first_name, c.c_last_name, count(ss.ss_ticket_number) as num_compras 
FROM store_sales ss 
JOIN customer c ON ss.ss_customer_sk = c.c_customer_sk 
GROUP BY c.c_first_name, c.c_last_name 
ORDER BY num_compras DESC 
LIMIT 20;
