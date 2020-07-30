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

# Sysmon

System Monitor (Sysmon) is a Windows system service and device driver that, once installed on a system, remains resident across system reboots to monitor and log system activity to the Windows event log. It provides detailed information about process creations, network connections, and changes to file creation time. By collecting the events it generates using Windows Event Collection or SIEM agents and subsequently analyzing them, you can identify malicious or anomalous activity and understand how intruders and malware operate on your network.

Note that Sysmon does not provide analysis of the events it generates, nor does it attempt to protect or hide itself from attackers.

