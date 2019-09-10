### MONITORING USING MODULE MSQL

```
- module: mssql
  metricsets:
    - "transaction_log"
    - "performance"
  hosts: ["sqlserver://<USER_BD>:<PASS_BD>@<IP_BD>"]
  period: 10m
```

Execute this command into MSQL for enabled special permission (View Server State) to <USER_BD>.

```
USE MASTER
GO
GRANT VIEW SERVER STATE TO "<USER_BD>"
```
