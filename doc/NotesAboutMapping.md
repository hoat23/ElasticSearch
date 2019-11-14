
### Adding a new type data a exist field

```
#For version < 7.0
PUT my_index-000001/_mapping/doc
{
  "properties": {
    "MY_FIELD": {
      "type": "text",
      "fields": { "keyword": { "type": "keyword" } }
    }
  }
}

#For version >= 7.0
PUT my_index-000001/_mapping
{
  "properties": {
    "MY_FIELD": {
      "type": "text",
      "fields": { "keyword": { "type": "keyword" } }
    }
  }
}
```
#Compatibility old datetime with version 7.0+
```
{
  "properties": {
    "@timestamp": {
      "type": "date"
    },
    "datetime": {
      "type": "date",
      "format": "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
    }
  }
}
```
