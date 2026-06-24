INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q9/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
SELECT d.d_year, d.d_moy, sum(ss.ss_net_paid) as total_ventas,
       RANK() OVER (PARTITION BY d.d_year ORDER BY sum(ss.ss_net_paid) DESC) as ranking_mensual
FROM store_sales ss 
JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk 
GROUP BY d.d_year, d.d_moy
ORDER BY d.d_year, ranking_mensual;
