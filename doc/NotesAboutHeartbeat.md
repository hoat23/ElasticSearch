# HeartBeat

# Configurate heartbeat.yml

Configuring Hearbeat to dynamically load modules. This refresh every 60 seconds.

```
heartbeat.config.monitors:
  path: ${path.config}/monitors.d/*.yml
  reload.enabled: true
  reload.period: 60s
```

Customizing the origin data (heartbeat.yml):

```
processors:
  - add_fields:
      target: observer
      fields:
        ip: 192.168.1.23
        id: heartbeat_192.168.1.23
        name: heartbeat_monitoring
        type: heartbeat
        geo:
          name: Heartbeat-lima-pe
          location:
            lat: -12.094800
            lon: -77.038676
          continent_name: South America
          country_iso_code: PE
          region_name: Lima
          region_iso_code: LI
          city_name: Lima
```


