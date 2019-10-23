# Validación de la configuración snmp

Instalar el el paquete de monitoreo snmp de linux, según el sistema operativo.
En sistemas RPM/RHEL/Centos:
```
yum install net-snmp-utils
```
En sistemas DEV/DEBIAN/UBUNTU
```
apt install snmp
```

Ejecutar el siguiente comando ("-v2c" para la versión 2 y "-v1" para la versión 1):

```
snmpwalk -v2c -c [comunidad] [IP]
```

Si recibe una respuesta difrente a

```
Timeout: No response from [IP]
```
La validación de la configuración snmp se realizo con exito

### GET, WALK AND TRANSLATE SNMP IN CENTOS
```
snmpget -v?  -c xxxxxx <ip/fqdn> yourMIB::<OID name>.
------------------------------------------------------------------------------------
example: snmpget -v1  -c public 192.168.1.32 PowerNet-MIB::emsProbeStatusProbeTemperature.
snmpget -v1  -c public 192.168.1.32 1.3.6.1.2.1.1.1.0

Similarly you can use snmpwalk:
Example:
snmpwalk -v1  -c public 192.168.1.32 1.3.6.1.2.1.1.1.0

To check if your  MIB was correctly installed and can be decoded use snmptranslate
Example:
snmptranslate -Td SNMPv2-SMI::enterprises.318.1.1.10.2.3.2.1.4.1
----------------------------------------------------------------------
snmpwalk -v1  -c public 192.168.1.32 1.3.6.1.2.1.1.1.0
RFC1213-MIB::sysDescr.0 = STRING: "APC Web/SNMP Management Card (MB:v3.9.2 PF:v3.6.1 PN:apc_hw02_aos_361.bin AF1:v3.5.8 AN1:apc_hw02_sumx_358.bin MN:AP9618 HR:A10 SN: BA0936024172 MD:09/05/2009) (Embedded PowerNet SNMP Agent SW v2.2 compatible)"

snmpget -v1  -c public 192.168.1.36 SNMPv2-SMI::enterprises.318.1.1.10.1.2.2.1.2.1
PowerNet-MIB::emConfigProbeName.1 = STRING: "backroom_amb"

snmpget -v1  -c public 192.168.1.32 1.3.6.1.2.1.1.1.0
RFC1213-MIB::sysDescr.0 = STRING: "APC Web/SNMP Management Card (MB:v3.9.2 PF:v3.6.1 PN:apc_hw02_aos_361.bin AF1:v3.5.8 AN1:apc_hw02_sumx_358.bin MN:AP9618 HR:A10 SN: BA0936024172 MD:09/05/2009) (Embedded PowerNet SNMP Agent SW v2.2 compatible)

snmptranslate -Td SNMPv2-SMI::enterprises.318.1.1.10.2.3.2.1.4.1
PowerNet-MIB::iemStatusProbeCurrentTemp.1
iemStatusProbeCurrentTemp OBJECT-TYPE
  -- FROM    PowerNet-MIB
  SYNTAX    INTEGER
  MAX-ACCESS    read-only
  STATUS    mandatory
  DESCRIPTION    "The current temperature reading from the probe displayed
       in the units shown in the 'iemStatusProbeTempUnits' OID
       (Celsius or Fahrenheit)."
::= { iso(1) org(3) dod(6) internet(1) private(4) enterprises(1) apc(318) products(1) hardware(1) environmentalMonitor(10) integrated(2) iemStatus(3) iemStatusProbesTable(2) iemStatusProbesEntry(1) iemStatusProbeCurrentTemp(4) 1 }

```
