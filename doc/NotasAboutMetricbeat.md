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
##### ERRORS 
Error by credentials: error scanning single result: mssql: The server principal "USER_BD" is not able to access the database "BD_My_DataBaSe" under the current security context.
