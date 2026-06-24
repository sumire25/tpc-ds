INSERT OVERWRITE DIRECTORY "s3://onpe-datalake-mx/query_results/tpc-ds/hive/q5/" ROW FORMAT DELIMITED FIELDS TERMINATED BY "," 
WITH ranked_products AS (
    SELECT s.s_store_name, i.i_product_name, sum(ss.ss_net_paid) as total_ventas,
           ROW_NUMBER() OVER (PARTITION BY s.s_store_name ORDER BY sum(ss.ss_net_paid) DESC) as rnk
    FROM store_sales ss 
    JOIN store s ON ss.ss_store_sk = s.s_store_sk 
    JOIN item i ON ss.ss_item_sk = i.i_item_sk
    GROUP BY s.s_store_name, i.i_product_name
)
SELECT s_store_name, i_product_name, total_ventas 
FROM ranked_products 
WHERE rnk = 1;
