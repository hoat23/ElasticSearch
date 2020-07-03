# Elasticsearch

Elastic Support Matrix at https://www.elastic.co/support/matrix. The installation instructions for all the supported platforms can be found in the Installing Elasticsearch documentation https://www.elastic.co/guide/en/elasticsearch/reference/7.0/install-elasticsearch.html

## Elasticsearch configuration JVM heap size

```
# Xms represents the initial size of total heap space
# Xmx represents the maximum size of total heap space
-Xms1g
-Xmx1g
```

You rarely need to change the Java Virtual Machine (JVM) options unless the Elasticsearch server is moved to production. These settings can be used to improve performance. When configuring heap memory, please keep in mind that the Xmx setting is 32 GB at most, and no more than 50% of the available RAM.

## Config Logging files

log4j2.properties: Elasticsearch uses Log4j 2 for logging. The log file location is made from three given properties, ${sys:es.logs.base_path}, ${sys:es.logs.cluster_name}, and ${sys:es.logs.node_name} in the log4j2.properties file, as shown in the code block:

```
appender.rolling.fileName = ${sys:es.logs.base_path}${sys:file.separator}${sys:es.logs.cluster_name}.log
```

For example, our installed directory is ~/elasticsearch-7.0.0. Since no base path is specified, the default value of ~/elasticsearch-7.0.0/logs is used. Since no cluster name is specified, the default value of elasticsearch is used. The log file location setting appender.rolling.filename will generate a log file named ~/elasticsearch-7.0.0/logs/elasticsearch.log

## Comunicate with Elasticsearch usign API

```
curl -XGET 'http://localhost:9200'
{
 "name" : "wai",
 "cluster_name" : "elasticsearch",
 "cluster_uuid" : "7-fjLIFkQrednHgFh0Ufxw",
 "version" : {
 "number" : "7.0.0",
 "build_flavor" : "default",
 "build_type" : "tar",
 "build_hash" : "a30e8c2",
 "build_date" : "2018-12-17T12:33:32.311168Z",
 "build_snapshot" : false,
 "lucene_version" : "8.0.0",
 "minimum_wire_compatibility_version" : "6.6.0",
 "minimum_index_compatibility_version" : "6.0.0-beta1"
 },
 "tagline" : "You Know, for Search"
}
```

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
 ## WARNING: No modificar el archivo "jupyter_notebook_config.py".
 
 ## Requirements
 It's in /bin/requirements.txt
 
 ```
 pip install -r requirements.txt
 ```
