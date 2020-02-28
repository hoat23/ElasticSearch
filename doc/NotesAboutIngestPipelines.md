#### 

```
PUT _ingest/pipeline/add_timestamp_elk
{
  "description" : "Pipeline for calculate latency between Logstash and Elasticsearch and set timestamp when document arrived to logstash.",
  "processors" : [
    {
      "script": {
        "source": """
          def data_json = [];
          def sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
          def timestamp_elasticsearch =  new Date();
          def timestamp_logstash = sdf.parse(ctx['@timestamp']);
          ctx['@timestamp'] = timestamp_elasticsearch;
          ctx['logstash_timestamp'] = timestamp_logstash;
          ctx['elastic_latency'] = timestamp_elasticsearch.getTime() - timestamp_logstash.getTime();
        """
      }
    }
  ]
}
```

```
PUT my-index/_doc/my-id?pipeline=my_pipeline_id
{
  "foo": "bar"
}
```

```
PUT _ingest/pipeline/reindex_metricbeat
{
  "description": """
  This pipeline force writing document into a other index.
  Author: deinerzapata@supra.com.pe
  """,
  "processors": [
    {
      "script": {
        "source": """
        String index = ctx._index;
        if (index == 'metricbeat-7.3.0') {
          ctx._index = 'metricbeat-group01-write';
        }
        
        """
      }
    }
    ]
}
```
```
POST _template/metricbeat-7.3.0
{
  "order": 6,
  "index_patterns": ["metricbeat-7.3.0*"],
  "settings": {
    "default_pipeline": "reindex_metricbeat"
  }
}
```

```
PUT _ingest/pipeline/drop_dont_exists_utmaction
{
  "processors": [
    {
      "drop": {
        "if": """
          if( (ctx.utmaction == null || ctx.utmaction == '' ) && ctx.type == 'traffic'){
            return true;
          }else{
            return false;
          }
    """
      }
    }
  ]
}
```
