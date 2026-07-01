Ive runned the main.tf pipeline. Now i want a simple, efficient, modular, high performance and resilient pipeline,
with good data engineeer practices, to run new queries in both spark and hive. Create a new folder for this.
And also save its running metrics of each individual queries as time, cpu and memory usage, core vcpu seconds, etc, in a csv file:
For now i want Hive and spark queries for the following, write optimized queries for them, to be saved on the s3 folder s3://onpe-datalake-mx/query_results/tpc-ds/ :
- Top 20 clientes con mayor número de compras. 
- Ventas por tienda.
- Ventas por mes 
- Ventas por día de lasemana 
- Top productos por tienda 
- Ticket promedio por cliente. 
- Productos con mayor ingreso generado 
- Top clientes por gasto total 
- Ranking mensual de ventas 
