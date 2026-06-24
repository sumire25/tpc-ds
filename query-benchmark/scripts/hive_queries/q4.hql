INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q4/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
SELECT d.d_day_name, sum(ss.ss_net_paid) as total_ventas 
FROM store_sales ss 
JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk 
GROUP BY d.d_day_name
ORDER BY total_ventas DESC;
