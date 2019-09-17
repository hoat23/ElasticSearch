
### Tree Structure in Bucket-Aggregation
```
aggregations.clientes.buckets.[]
	sedes.buckets.[]
	   ip_group.buckets.[]
	   	   global_info.hits.hits.[]
	   	   monitor_status.buckets[]
```

```
A     = [ "aggregations": [ "clientes": [ "buckets":[Bx], "sum_other_doc_count":0, "doc_count_error_upper_bound": 0 ] ] ]
Bx    = "aggregations.clientes.buckets"
```

```
AA    = [ "key": " < name_client >", "doc_count": 12,     "ip_group": ["buckets":   [BBx], "sum_other_doc_count": 0, "doc_count_error_upper_bound": 0 ] ]
BBx   = "AA.ip_group.buckets"
```

```
AAA   = [ "key": "<name_ip_group>" , "doc_count": 12, "reporting_ip": ["buckets":  [BBBx], "sum_other_doc_count": 0, "doc_count_error_upper_bound": 0 ] ]
BBBx  = "AAA.reporting_ip.buckets"
```

```
AAAA  = [ "key": "<name_repor_ip>" , "doc_count": 12, "monitor_status": ["buckets":  [BBBBx], "sum_other_doc_count": 0, "doc_count_error_upper_bound": 0 ], 
       "global_info": ["hits": [ "total": 12, "max_score": null, "hits": [ ["_index": "<index>", "_score": null , "_source": [ . . . ]] ] ] ] ]
BBBBx = "AAAA.monitor_status.buckets"
G_INFO= "AAAA.global_info.hits.hits.0"
```
 
