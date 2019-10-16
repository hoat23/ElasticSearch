# CONFIGURACIÓN DE INDEX LIFECYCLE MANAGEMENT


### Crear indice
```
PUT my_index-000001
{
  "aliases": {
    "my_index-**alias_write**: {}
  }
}
```

### Cargar datos en el indice
```
PUT my_index-alias_write/_doc/1
{
  "myfield01": "myvalue01"
}
```

### Crear politica ILM 
```
PUT _ilm/policy/test-index-policy
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
      "lifecycle.name": "my_index_policy",
      "lifecycle.rollover_alias": "my_index-alias_write"
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
POST my_index-alias_write/_rollover
```
