# Elasticsearch

Elastic Support Matrix at https://www.elastic.co/support/matrix. The installation instructions for all the supported platforms can be found in the Installing Elasticsearch documentation https://www.elastic.co/guide/en/elasticsearch/reference/7.0/install-elasticsearch.html

## Elasticsearch configuration JVM heap size
´´´
# Xms represents the initial size of total heap space
# Xmx represents the maximum size of total heap space
-Xms1g
-Xmx1g
´´´
You rarely need to change the Java Virtual Machine (JVM) options unless the Elasticsearch server is moved to production. These settings can be used to improve performance. When configuring heap memory, please keep in mind that the Xmx setting is 32 GB at most, and no more than 50% of the available RAM.

# Python-Elasticsearch

Code to upload, download or process data in Elasticsearh

## Descripción:

Servidor Jupyter instalado en AWS que permite interactuar con la data de ElasticCloud, permite cargar datos, descargar datos, procesar datos o hacer pruebas rápidas de algoritmos codificados en Python (por el momento) y la data de ElasticCloud.

## Estructura de carpetas:

```
 |--bin: Contiene los ejecutables y programas.
 |
 |--nbconfig: Contiene archivos de configuración propios de Jupyter.
 |
 |--doc: Contiene archivos y documentos necesarios externos que se requieran cargar al servidor.
 |
 |--tmp: Contiene documentos temporales generados durante la ejecución de cualquier ejecutable o programa.
 |
 |--notebook: Contiene los Notebok para testear codigo Python.
 ```
 ## WARNNING: No modificar el archivo "jupyter_notebook_config.py".
