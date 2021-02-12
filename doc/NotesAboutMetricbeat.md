# METRICBEAT
## Run in debug mode
```
metricbeat -e
```

## Start service 
In Ubuntu:
```
service metricbeat start
```
### FILE OF GLOBAL CONFIGURATION
```
# /etc/metricbeat/metricbeat.yml
# c:/ProgramaFiles/metricbeat/metricbeat.yml
```

Loading modules dynamically every 60 seconds.

```
metricbeat.config.modules:
  # Glob pattern for configuration loading
  path: ${path.config}/modules.d/*.yml
  # Set to true to enable config reloading
  reload.enabled: true
  # Period on which files under path should be checked for changes
  reload.period: 60s
```

### MONITORING USING MODULE MSSQL

```
- module: mssql
  metricsets:
    - "transaction_log"
    - "performance"
  hosts: ["sqlserver://<USER_DB>:<PASS_DB>@<IP_DB>"]
  period: 10m

# <USER_DB>: user credential of database.
# <PASS_DB>: password credential of database.
# <IP_DB>: IP of database
```

Execute this command into MSQL for enabled special permission (View Server State) to <USER_BD>.

```
USE MASTER
GO
GRANT VIEW SERVER STATE TO "<USER_BD>"
```
##### ERRORS 
Error by credentials: error scanning single result: mssql: The server principal "USER_BD" is not able to access the database "BD_My_DataBaSe" under the current security context.
