# Transform data in Elasticsearch

## Preview of a transform

```
POST _transform/preview
{
   ...
}
```

## Create a transform

```
PUT _transform/my_transform_name
{
   ...
}
```



## Update a transform

```
POST _transform/my_transform_name
{
   ...
}
```


## Examples

### Example 1: Reducing Traffic Logs
```
PUT _transform/ecs-fortigate-traffic-client
{
  "description": "Transform of traffic",
  "source": {
    "index": [
      "ecs-fortigate-client-write"
    ],
    "query": {
      "bool": {
        "should": [
          { "match": { "type": "traffic" } }
        ],
        "must": [
          { "range": { "@timestamp": { "gte": "now-2h" } } }
        ],
        "must_not": [
          { "match": { "event.code": "0000000020" } }
        ],
        "minimum_should_match": 1
      }
    }
  },
  "dest": {
    "index": "ecs-fortigate-traffic-client"
  },
  "frequency": "1m",
  "sync": { "time": { "field": "@timestamp", "delay": "60s" } },
  "pivot": {
    "group_by": {
      "observer_name": { "terms": { "field": "observer.name" } },
      "observer_ip": { "terms": { "field": "observer.ip" }
      },
      "timestamp": {
        "date_histogram": {
          "field": "@timestamp",
          "calendar_interval": "1m"
        }
      }
    },
    "aggregations": {
      "source_bytes": { "sum": { "field": "source.bytes" } },
      "destination_bytes": { "sum": { "field": "destination.bytes" } },
      "total_bytes": { "sum": { "field": "network.bytes" } }
    },
    "max_page_search_size": 10000
  }
}
```
