# Proyecto TPC-DS en AWS EMR

## Descripción del Proyecto
Este proyecto implementa un pipeline de datos utilizando el dataset TPC-DS a una escala de 10GB. El flujo de trabajo abarca la generación de datos, su transformación a formato columnar, la ejecución de modelos de machine learning y la evaluación de rendimiento de consultas distribuidas utilizando Spark y Hive en un cluster de AWS EMR.

## Arquitectura y Tecnologías
*   **AWS EMR**: Procesamiento distribuido.
*   **Terraform**: Infraestructura como código para desplegar los clusters.
*   **Amazon S3**: Almacenamiento de scripts, datos crudos, tablas particionadas y resultados.
*   **Apache Spark**: Conversión de datos, machine learning y ejecución de consultas SQL.
*   **Apache Hive**: Ejecución de consultas SQL.
*   **YARN**: Gestor de recursos del cluster utilizado para extraer métricas de consumo.

## Fases del Proyecto

### 1. Generación de Datos y Parquet
El pipeline comienza con un script que compila el toolkit de TPC-DS y genera los archivos de texto iniciales. Posteriormente, un job de Spark procesa estos datos y los convierte al formato Parquet. Durante esta etapa se aplica particionamiento por fecha en las fact tables principales para mejorar la eficiencia de las consultas.

### 2. Segmentación de Clientes con Machine Learning
Se utiliza Spark MLlib para realizar un análisis RFM (Recency, Frequency, Monetary) de los clientes. 
*   **Cálculo de Recency:** La "fecha actual" o de referencia se calcula dinámicamente obteniendo la fecha máxima de venta (`max_date`) existente en todo el dataset de `store_sales`. La recencia de cada cliente es la diferencia en días entre esa fecha máxima y su última compra.
*   El algoritmo K-Means agrupa a los clientes en 5 segmentos (`k=5`) basándose en su historial de compras. 
*   Los resultados se unen con la tabla `customer` y se guardan en S3.

### 3. Benchmarking de Consultas
El proyecto incluye un entorno aislado en el directorio `query_pipeline` para evaluar el rendimiento de nueve consultas analíticas.
*   Las consultas se ejecutan secuencialmente en Spark y Hive.
*   Un script en Python consulta la REST API de YARN tras cada ejecución para capturar métricas distribuidas exactas, específicamente `vcoreSeconds` y `memorySeconds`.
*   Los tiempos de ejecución y las métricas de consumo se consolidan en archivos de texto individuales por consulta.

## Ejecución

El proyecto está diseñado para funcionar en cuentas de AWS Academy Learner Lab, utilizando el IAM role `LabRole`.

Para desplegar el pipeline principal de generación de datos y machine learning:
```bash
terraform init
terraform apply -auto-approve
```

Para desplegar el entorno de benchmarking de consultas, navegue al directorio correspondiente y ejecute Terraform:
```bash
cd query_pipeline
terraform init
terraform apply -auto-approve
```
