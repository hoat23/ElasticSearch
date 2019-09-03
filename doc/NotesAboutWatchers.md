#Diferencias entre input y chain-input, teniendo como base un input simple.

INPUT SIMPLE
path_to_first_aggregation: ctx.payload.aggregations.[NAME_FIRST_AGGREGATION]

"input": {
	"search": {...}
}


INPUT CHAIN
path_to_first_aggregation: ctx.payload.CHAIN_FIRST.aggregations.[NAME_FIRST_AGGREGATIONS]
"input": {
	"chain": {
		"inputs": [
			"CHAIN_FIRST" : {
				{"search": {...}}
			}
		]
	}
}
