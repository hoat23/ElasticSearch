# CONFIGURACIÓN DE INDEX LIFECYCLE MANAGEMENT


### Crear indice
```
PUT my_index-000001
{
  "aliases": {
    "my_index-alias-write: {}
  }
}
```

### Cargar datos en el indice
```
PUT my_index-alias-write/_doc/1
{
  "myfield01": "myvalue01"
}
```

### Crear politica ILM 

The size (max_size: 5mb) is only the primary shard, don't include the replicas. 

```
PUT _ilm/policy/policy_index_management
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": { "max_size": "5mb" }
        }
      },
      "warm": {
        "actions": {
          "forcemerge": { "max_num_segments": 1 },
          "allocate" : {
            "require" : { "data": "warm" }
          }
        }
      },
      "delete": {
        "min_age": "1M",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### Agregar politica ILM a futuros indices usando template
```
PUT _template/my_index-template
{
  "index_pattern": ["my_index-*"],
  "order": 3,
  "settings": {
    "index": {
      "number_of_shards": 4,
      "number_of_replicas": 0,
      "refresh_interval": "5s",
      "lifecycle.name": "policy_index_management",
      "lifecycle.rollover_alias": "my_index-alias-write"
    }
  }
}
```
Validar obteniendo el template creado:
```
GET _template/my_index-template
```

### Realizar Rollover para que el nuevo indice creado se genere con las politicas ILM respectivas
```
POST my_index-alias-write/_rollover
```

### Linkear un indice antiguo con una politica ILM
```
PUT my_index-000023/_settings
{
  "index": {
     "lifecycle.name": "policy_index_management"
  }
}
```
