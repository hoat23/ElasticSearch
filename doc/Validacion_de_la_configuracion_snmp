# Validación de la configuración snmp

Instalar el el paquete de monitoreo snmp de linux, según el sistema operativo.
En sistemas RPM/RHEL/Centos:
´´´
yum install net-snmp-utils
´´´
En sistemas DEV/DEBIAN/UBUNTU
´´´
apt install snmp
´´´

Ejecutar el siguiente comando ("-v2c" para la versión 2 y "-v1" para la versión 1):

´´´
snmp -v2c -c [comunidad] [IP]
´´´

Si recibe una respuesta difrente a

´´´
Timeout: No response from [IP]
´´´
La validación de la configuración snmp se realizo con exito
