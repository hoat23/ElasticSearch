#Instalación de Logtash en Windows

1. Windows debe estar actualizado
2. Instalar Oracle Java Developmet Kit (JDK), no la Java Runtime (JRE)
3. Abrir el cmd y ejecutar "java --version", para validar la versión de Logstash instalada.
4. Descargar el binario de https://www.elastic.co/es/downloads/logstash y extraer el ZIP en C:\logstash\.
5. Crear un archivo en C:\logstash\bin\logstash.conf con el siguiente contenido.

```
input {
    # Accept input from the console.
    stdin{}
}

filter {
    # Add filter here. This sample has a blank filter.
}

output {
    # Output to the console.
    stdout {
            codec => "rubydebug"
    }
}
```

6. Iniciar el logstash, ejecutando el archivo batch, con el flag "-f" para definir la localización del archivvo de configuración.

```
c:\logstash\bin\logstash.bat -f c:\logstash\bin\logstash.conf
```
7. Para detener el logstash ejecutar "CTRL+C"

###Instalar Logstash como un servicio en Windows.

http://www.dissmeyer.com/2017/11/11/installing-logstash-on-windows/
