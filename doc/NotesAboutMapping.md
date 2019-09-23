
### Adding a new type data a exist field

```
PUT my_index-000001/_mapping/doc
{
  "properties": {
    "MY_FIELD": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    }
  }

```
