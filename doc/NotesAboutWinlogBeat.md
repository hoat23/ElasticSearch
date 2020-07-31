# WinlogBeat

## Installing WinglogBeat

Follow the installation steps according to the documentation and run like a Windows service.

- Download the Winlogbeat zip file from the downloads page.
- Extract the contents into C:\Program Files.
- Rename the winlogbeat-<version> directory to Winlogbeat.
- Open a PowerShell prompt as an Administrator (right-click on the PowerShell icon and select Run As Administrator).
- From the PowerShell prompt, run the following commands to install the service.
```
PS C:\Program Files\Winlogbeat> .\install-service-winlogbeat.ps1
```
If not work, try this command:

```
PowerShell.exe -ExecutionPolicy UnRestricted -File .\install-service-winlogbeat.ps1
```
https://www.elastic.co/guide/en/beats/winlogbeat/current/winlogbeat-installation.html

Show all list of services installed in your computer, sorted by status.
```
Get-Service "s*" | Sort-Object status
```
Searching WinlogBeat service:
```
Get-Service winlogbeat
```
If want see dependency of a service, just execute: 
```
Get-Service "WinRM" -RequiredServices
```
## Configuring WinglogBeat

### Using a API-Key for ingest data

```
POST /_security/api_key
{
  "name": "api_key_winglogbeat",
  "expiration": "1d", 
  "role_descriptors": { 
    "winglogbeat_write": {
      "cluster": ["all"],
      "index": [
        {
          "names": ["*"],
          "privileges": ["write"]
        }
      ]
    }
  }
}
```
The response return something like this:
```
{
  "id":"VuaCfGcBCdbkQm-e5aOx", 
  "name":"api_key_winglogbeat",
  "expiration":1544068612110, 
  "api_key":"ui2lp2axTNmsyakw9tvNnw" 
}
```

Then proceed to configure the winglogbeat.yml file with the "id" and "api_key" respectively.

```
output.elasticsearch:
  # Authentication credentials - either API key or username/password id:api_key.
  api_key: "VuaCfGcBCdbkQm-e5aOx:ui2lp2axTNmsyakw9tvNnw"
```
# Events in Windows

## event_logs.name

The name of the event log to monitor:
```
PS C:\User\Hoat23> Get-EventLogs *
```

The channels can also be specified. A channes is a named stream of events that transports events from an event source to an event log.
Here is an example showing how to list all channels using PowerShell.

```
PS C:\User\Hoat23> Get-EventLogs -ListLog * | Format-List -Property LogName
```

you must specify the fullname of the channel in the configuration file.

```
winlogbeat.event_logs:
  - name: Microsoft-Windows-Windows Firewall With Advanced Security/Firewall
```

To read events from an archived ".evtx" file
```
winlogbeat.event_logs:
  - name: 'C:\backup\sysmon-2019.08.evtx'
```

## event_logs.ignore_older

This option is useful when you are beginning to monitor an event log that contains older records that you would like to ignore. This field is optional.
```
winlogbeat.event_logs:
  - name: Application
    ignore_older: 168h
```

## event_logs.event_id

 The value is a comma-separated list. The accepted values are single event IDs to include (e.g. 4624), a range of event IDs to include (e.g. 4700-4800), and single event IDs to exclude (e.g. -4735)
```
winlogbeat.event_logs:
  - name: Security
    event_id: 4624, 4625, 4700-4800, -4735
```

The filter shown below is equivalent to event_id: 903, 1024, 4624 but can be expanded beyond 22 event IDs.
```
winlogbeat.event_logs:
  - name: Security
    processors:
      - drop_event.when.not.or:
        - equals.winlog.event_id: 903
        - equals.winlog.event_id: 1024
        - equals.winlog.event_id: 4624
```

## event_logs.level

- critical, crit
- error, err
- warning, warn
- information, info
- verbose
```
winlogbeat.event_logs:
  - name: Security
    level: critical, error, warning
```

# Sysmon

System Monitor (Sysmon) is a Windows system service and device driver that, once installed on a system, remains resident across system reboots to monitor and log system activity to the Windows event log. It provides detailed information about process creations, network connections, and changes to file creation time. By collecting the events it generates using Windows Event Collection or SIEM agents and subsequently analyzing them, you can identify malicious or anomalous activity and understand how intruders and malware operate on your network.

Note that Sysmon does not provide analysis of the events it generates, nor does it attempt to protect or hide itself from attackers.

# References

https://www.binarydefense.com/using-sysmon-and-etw-for-so-much-more/

https://github.com/SwiftOnSecurity/sysmon-config/blob/master/sysmonconfig-export.xml

https://medium.com/@olafhartong/endpoint-detection-superpowers-on-the-cheap-part-1-e9c28201ac47

https://www.youtube.com/watch?v=7dEfKn70HCI

https://cyberwardog.blogspot.com

https://lolbas-project.github.io

https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon


