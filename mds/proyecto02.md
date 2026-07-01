## **UNIVERSIDAD NACIONAL DE SAN AGUSTÍN DE AREQUIPA** 

**ESCUELA PROFESIONAL DE CIENCIA DE LA COMPUTACIÓN** 

**CURSO: BIGDATA 2026A** 

## **TRABAJO UNIDAD II** 

## **Data Engineering para Retail utilizando Hive, Spark y LLM** 

**10 de junio del 2026** 

## **CONTENIDO DE LA GUÍA** 

## **I. MARCO CONCEPTUAL** 

## **I.1. Big Data y el procesamiento distribuido** 

El crecimiento exponencial de los datos generados por empresas, redes sociales, sensores y plataformas digitales ha impulsado el desarrollo de tecnologías capaces de almacenar y procesar grandes volúmenes de información. Este fenómeno es conocido como Big Data y suele caracterizarse mediante las cinco V: volumen, velocidad, variedad, veracidad y valor. En el contexto empresarial, especialmente en el sector retail, millones de transacciones pueden generarse diariamente, haciendo inviable el procesamiento mediante sistemas tradicionales. 

El procesamiento distribuido consiste en dividir una tarea compleja en múltiples subtareas que pueden ejecutarse simultáneamente sobre diferentes nodos de un clúster. Esta estrategia permite reducir los tiempos de procesamiento y mejorar la escalabilidad del sistema. Frameworks como Hadoop y Spark implementan este paradigma para resolver problemas relacionados con el análisis masivo de datos. 

: 

## **I.2. Data Warehouse** 

Un Data Warehouse es un sistema diseñado para almacenar información histórica y facilitar el análisis de datos. A diferencia de las bases de datos transaccionales, un Data Warehouse está optimizado para consultas analíticas y agregaciones. 

Generalmente se utilizan modelos dimensionales compuestos por: 

- Tablas de hechos. 

- Tablas dimensión. 

En el contexto del retail, una tabla de ventas puede relacionarse con dimensiones como clientes, productos, tiendas, promociones y fechas. 

## **I.3. Benchmark TPC-DS** 

TPC-DS es un benchmark desarrollado por el Transaction Processing Performance Council para evaluar sistemas de Data Warehouse y plataformas analíticas. Simula un entorno comercial con múltiples canales de venta, incluyendo tiendas físicas, ventas web y catálogos. 

TPC-DS proporciona un generador de datos capaz de crear datasets desde algunos gigabytes hasta varios terabytes, permitiendo evaluar el rendimiento de diferentes tecnologías analíticas bajo escenarios realistas. 

Para este proyecto se utilizarán tablas generadas a partir de TPC-DS, simulando un entorno retail con millones de transacciones. 

## **I.4. Análisis Agéntico de datos (Agentic Analytics)** 

El crecimiento exponencial de los datos empresariales ha generado la necesidad de desarrollar mecanismos que permitan acceder a la información de manera más eficiente y natural. Tradicionalmente, los sistemas analíticos requieren que los usuarios conozcan lenguajes de consulta como SQL y comprendan la estructura interna de las bases de datos. Sin embargo, los recientes avances en modelos de lenguaje y sistemas inteligentes han dado origen a nuevas formas de interacción conocidas como análisis agéntico o Agentic Analytics. 

El análisis agéntico es un paradigma que combina modelos de lenguaje, herramientas analíticas y mecanismos de automatización para facilitar la exploración y consulta de grandes volúmenes de datos. En lugar de escribir consultas manualmente, el usuario puede expresar sus necesidades en lenguaje natural, mientras el sistema interpreta la intención, determina las operaciones necesarias y utiliza las herramientas adecuadas para obtener los resultados. 

A diferencia de un chatbot convencional, un sistema de análisis agéntico no se limita a generar texto, sino que puede interactuar con fuentes de datos, ejecutar consultas y combinar múltiples procesos para resolver problemas específicos del dominio de análisis. 

Estos representan una evolución de los asistentes tradicionales, permitiendo que un modelo de lenguaje planifique tareas, invoque herramientas especializadas y combine múltiples pasos para resolver problemas complejos. 

En el contexto de análisis de datos, un agente puede recibir preguntas en lenguaje natural como: 

_"¿Cuáles fueron los 10 productos más vendidos durante el último trimestre?"_ 

El agente interpreta la intención del usuario, identifica las tablas involucradas, genera automáticamente una consulta SQL compatible con Hive o Spark, ejecuta la consulta y presenta los resultados. 

Para este proyecto, la capa agéntica tendrá un alcance controlado basado en el paradigma de **skills** , donde cada habilidad implementa una función específica, por ejemplo: 

- Identificación de intención. 

- Generación de SQL. 

- Ejecución de consultas. 

- Presentación de resultados. 

Este enfoque introduce a los estudiantes en las tendencias actuales de Data Engineering y Analytics, integrando Big Data con Inteligencia Artificial Generativa sin incrementar excesivamente la complejidad del proyecto. 

## **II. EJERCICIOS/PROBLEMAS PROPUESTOS** 

## **1. Objetivo.** 

Implementar una plataforma de análisis de datos sobre un Data Warehouse Retail basado en TPC-DS utilizando Apache Hive y Apache Spark sobre Amazon EMR, realizando un análisis comparativo de rendimiento e incorporando una capa de análisis agéntico capaz de interpretar consultas en lenguaje natural y generar consultas SQL automáticamente. 

## **2. Objetivos específicos** 

Para efectos del trabajo deberán seguir el siguiente flujo de trabajo recomendado. 

- a) Implementar un Data Warehouse Retail utilizando TPC-DS. 

- b) Crear las tablas necesarias en Hive. 

- c) Realizar consultas analíticas mediante HiveQL. 

- d) Implementar las mismas consultas utilizando Spark SQL. 

- e) Comparar el rendimiento de ambas tecnologías. 

- f) Diseñar una capa de análisis agéntico basada en skills. 

- g) Integrar un modelo LLM para generación automática de consultas. 

- h) Analizar ventajas y limitaciones del enfoque propuesto. 

## **3. Datasets** 

Documentación: https://www.tpc.org/tpcds/ Github: https://github.com/gregrahn/tpcds-kit 

*Generar 10GB de data o usar datasets ya generados por tpc de mas de 10GB. 

## **4. Tablas Obligatorias** 

- customer 

- item 

- store 

- date_dim 

- store_sales 

## **5. API Gemini.** 

Los estudiantes podrán utilizar Gemini para generar automáticamente consultas SQL. 

- API Key: https://aistudio.google.com/api keys 

Documentación: https://ai.google.dev/gemini-api/docs 

## **6. Actividades** 

- 6.1 Consultas en Hive y Spark: 

- Top 20 clientes con mayor número de compras. 

- Ventas por tienda. 

- Ventas por mes 

- Ventas por día de lasemana 

- Top productos por tienda 

- Ticket promedio por cliente. 

- Productos con mayor ingreso generado 

- Top clientes por gasto total 

- Ranking mensual de ventas 

- 6.2 Consultas Agénticas: 

- Cuales fueron los cinco productos mas vendidos? 

- Que tienda tuvo mayores ventas? 

- Cuál fué el mes con mayores ingresos? 

- Cuales son los diez mejores clientes? 

- Que productos generó mayores ingresos? 

- Realizar 5 consultas en lenguaje natural. 

- 6.3 Realizar comparación Hive vs Sparck 

- Tiempo de ejecución 

- Uso de CPU 

- Uso de memoria 

6.4 Realizar comparaciónmanual vs análisis agéntico. 

*El plus de proyecto se dará puntaje adicional por visualización, gráficos, insight. 

## **IV. ENTREGABLES** 

Al finalizar el estudiante deberá entregar archivo .pdf con el resultado de la actividad. Coloque su nombre en la parte superior del archivo. 

Debe subirlo al aula virtual o al classroom asignado hasta la hora indicada por el profesor. 

• IMPORTANTE En caso de copia o plagio o generación automática o similares todos los alumnos implicados tendrán sanción en toda la evaluación del curso. 

