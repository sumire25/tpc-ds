-- 05 - Top productos por tienda (top 10 per store)
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

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/hive/05_top_products_by_store'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
SELECT store_sk, store_name, item_sk, product_name, category, total_sales, rk
FROM (
    SELECT /*+ MAPJOIN(s), MAPJOIN(i) */
        ss.ss_store_sk          AS store_sk,
        s.s_store_name          AS store_name,
        ss.ss_item_sk           AS item_sk,
        i.i_product_name        AS product_name,
        i.i_category            AS category,
        ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales,
        RANK() OVER (PARTITION BY ss.ss_store_sk ORDER BY SUM(ss.ss_ext_sales_price) DESC) AS rk
    FROM store_sales ss
    JOIN store s ON ss.ss_store_sk = s.s_store_sk
    JOIN item  i ON ss.ss_item_sk  = i.i_item_sk
    GROUP BY ss.ss_store_sk, s.s_store_name, ss.ss_item_sk, i.i_product_name, i.i_category
) t
WHERE rk <= 10
ORDER BY store_sk, rk;
