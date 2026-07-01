-- 04 - Ventas por dia de la semana
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

INSERT OVERWRITE DIRECTORY 's3://onpe-datalake-mx/query_results/tpc-ds/hive/04_sales_by_weekday'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
SELECT /*+ MAPJOIN(d) */
    d.d_dow,
    d.d_day_name,
    ROUND(SUM(ss.ss_ext_sales_price), 2) AS total_sales
FROM store_sales ss
JOIN date_dim d ON ss.ss_sold_date_sk = d.d_date_sk
GROUP BY d.d_dow, d.d_day_name
ORDER BY d.d_dow;
