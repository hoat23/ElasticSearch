## Simple - One Field

```
POST _reindex?slices=3
{
  "source": {"index": "my_src_index"},
  "dest": {"index": "my_dst_index"}
}

POST _reindex?slices=3
{
  "source": {
    "index": "my_src_index-*",
    "type": "doc", 
    "query": {
      "term": { "my_field": "my_value" }
    }
  },
  "dest": {
    "index": "my_dst_index"
  }
}
```

## Complex - Upgrading some fields

```
POST _reindex?slices=3&wait_for_completion=false&conflicts=proceed
{
  "source": {
    "index": ["my_src_index-01", "my_src_index-02", "my_src_index-03"]
  },
  "dest": {
    "index": "my_dst_index"
  },
  "script": {
	 "inline": """
	      ctx._source.my_field_01 = "value_01"; 
	      ctx._source.my_field_02 = "value_02";
	      """,
	"lang": "painless"
  }
}
```
