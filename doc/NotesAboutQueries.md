
### Kill current querys
```
POST /_cache/clear
```

### Getting totals hits by query

```
GET filebeat-7.2.0-2019.07.18-000001/_search
{
  "track_total_hits": true
}
```

### Update by query : using slices (faster)

```
POST my_index/_update_by_query?conflicts=proceed&slices=4&wait_for_completion
{
  "script": {
    "inline": """
    String value = ctx._source['srcip'];
    ctx._source['user']= value;
    ctx._source['fuente']= 'ip';
    ctx._source['client_ip'] = '{params.client_ip}';
    """,
    "params": {
       "field": "client_ip
    }
  }
  ,
  "query": {
    "bool": {
      "must_not":[{"exists": {"field":"user"}}]
    }
  }
}
```


