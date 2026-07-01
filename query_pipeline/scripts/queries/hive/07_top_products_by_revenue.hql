-- 07 - Productos con mayor ingreso generado
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

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/hive/07_top_products_by_revenue'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
SELECT /*+ MAPJOIN(i) */
    ss.ss_item_sk,
    i.i_product_name,
    i.i_category,
    i.i_brand,
    ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_revenue
FROM store_sales ss
JOIN item i ON ss.ss_item_sk = i.i_item_sk
GROUP BY ss.ss_item_sk, i.i_product_name, i.i_category, i.i_brand
ORDER BY total_revenue DESC
LIMIT 20;
