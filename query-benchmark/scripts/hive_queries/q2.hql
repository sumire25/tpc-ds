INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q2/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
SELECT s.s_store_name, sum(ss.ss_net_paid) as total_ventas 
FROM store_sales ss 
JOIN store s ON ss.ss_store_sk = s.s_store_sk 
GROUP BY s.s_store_name
ORDER BY total_ventas DESC;
