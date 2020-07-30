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


