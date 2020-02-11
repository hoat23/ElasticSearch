
### Kill current querys
```
POST /_cache/clear
```

### Getting totals hits in by query

```
GET filebeat-7.2.0-2019.07.18-000001/_search
{
  "track_total_hits": true
}
```

### Update by query : using slices (faster)

```
POST syslog-auna/_update_by_query?conflicts=proceed&slices=4
{
  "script": {
    "inline": """
    String value = ctx._source['srcip'];
    ctx._source['user']= value;
    ctx._source['fuente']= 'ip';
    """
  }
  ,
  "query": {
    "bool": {
      "must_not":[{"exists": {"field":"user"}}]
    }
  }
}
```

