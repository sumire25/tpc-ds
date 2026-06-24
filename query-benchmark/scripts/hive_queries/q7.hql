INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q7/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
SELECT i.i_product_name, sum(ss.ss_net_paid) as ingresos 
FROM store_sales ss 
JOIN item i ON ss.ss_item_sk = i.i_item_sk 
GROUP BY i.i_product_name 
ORDER BY ingresos DESC 
LIMIT 20;
