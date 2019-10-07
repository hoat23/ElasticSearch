
### ERROR IN MODULE MACHINE LEARNING XPACK
```
"{\"error\":{\"root_cause\":[{\"type\":\"status_exception\",\"reason\":\"Could not open job because no ML nodes with sufficient capacity were found\"}],\"type\":\"status_exception\",\"reason\":\"Could not open job because no ML nodes with sufficient capacity were found\",\"caused_by\":{\"type\":\"illegal_state_exception\",\"reason\":\"Could not open job because no suitable nodes were found, allocation explanation [persistent task [xpack/ml/job] cannot be assigned [no persistent task assignments are allowed due to cluster settings]]\"}},\"status\":429}"
Error: "{\"error\":{\"root_cause\":[{\"type\":\"status_exception\",\"reason\":\"Could not open job because no ML nodes with sufficient capacity were found\"}],\"type\":\"status_exception\",\"reason\":\"Could not open job because no ML nodes with sufficient capacity were found\",\"caused_by\":{\"type\":\"illegal_state_exception\",\"reason\":\"Could not open job because no suitable nodes were found, allocation explanation [persistent task [xpack/ml/job] cannot be assigned [no persistent task assignments are allowed due to cluster settings]]\"}},\"status\":429}"
    at Object.errorNotify [as error] (https://my_cluster.us-east-1.aws.found.io:9243/bundles/commons.bundle.js:3:95946)
    at https://my_cluster.us-east-1.aws.found.io:9243/bundles/commons.bundle.js:3:334452
    at Array.forEach (<anonymous>)
    at showResults (https://my_cluster.us-east-1.aws.found.io:9243/bundles/commons.bundle.js:3:334385)
    at https://my_cluster.us-east-1.aws.found.io:9243/bundles/commons.bundle.js:3:331818
```

Setting configuration

```
PUT /_cluster/settings
{
	"transient": {
		"cluster.persistent_tasks.allocation.enable": "all"
	}
}
```
