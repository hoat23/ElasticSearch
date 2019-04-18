# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Description: Procesar las alertas generadas
#######################################################################################
import sys
from datetime import datetime
#######################################################################################
def bytesELK2json(data,codification='utf-8'):
    d_dict = {}
    try:
        if type(data)==bytes:
            d_str = data.decode(codification)
        else:
            d_str = data
        d_str = d_str.replace("false","False")
        d_dict = eval(d_str) # casting string->json
    except:
       print("ERROR | bytes2ELK2json <{1}>type={0} ".format( type(data) , len(data) ))
    finally:
       return d_dict
#######################################################################################
def download_configuration_from_elk(elk):
    dict_client_ip = {}
    logstash = {}
    data_query = { #GET index_configuration/_search?filter_path=hits.hits._source.logstash
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "dict_client_ip"}},
                    {"exists": {"field": "logstash"}}
                ]
            }
        }
    }
    
    data_response = elk.req_get(elk.get_url_elk()+"/index_configuration/_search?filter_path=hits.hits._source",data=data_query)['hits']['hits'][0]['_source']
    if len(data_response)<0:
        print("ERROR | {0} download_configuration | Failed to download data from elasticsearch.".format(datetime.utcnow().isoformat()))
    
    if 'dict_client_ip' in data_response: 
        dict_client_ip =  data_response['dict_client_ip']
    else:
        print("ERROR | {0} download_configuration | 'dict_client_ip' key don't exists in json response.".format(datetime.utcnow().isoformat()))
    
    if 'logstash' in data_response:
        logstash = data_response['logstash']
    else:
        print("ERROR | {0} download_configuration | 'logstash' key don't exists in json response.".format(datetime.utcnow().isoformat()))
    
    return dict_client_ip, logstash
#######################################################################################
def enrich_data_from(list_keys,list_key_to_add,dictionary):
    return {}
#######################################################################################
def build_watcher(label_watch_id="heartbeat_ping", indices = ["heartbeat-*"], interval="2m",window_time="4m"):
    query = {
        "bool" : {
            "filter" : [
            { "term" : { "monitor.status" : "down" } },
            { "range" : {
                "@timestamp" : {
                    "from" : "now-" + window_time,
                    "to" : "now"
                }
                }
            }]
        }
    }

    aggs =  {
        "num_device_by_ip" : {
            "cardinality" : {
            "field" : "devip"
            }
        }
    }

    body_webhook = """
            {
                "num_type": "00001",
                "path_element": "{{ctx.metadata.path_element}}",
                "last_execution_time": "{{ctx.execution_time}}",
                "monitoring_tool": "Elastic Watcher",
                "id": "{{ctx.id}}",
                "label_watch_id":"{{ctx.metadata.label_watch_id}}",
                "watch_id": "{{ctx.watch_id}}",
                "payload": {{#toJson}}ctx.payload{{/toJson}} 
            }
            """

    watcher = {
    "metadata" : {
        "path_element" : "payload.aggregations.clientes.[buckets].sedes.[buckets].ip_s.[buckets].key",
        "label_watch_id" : label_watch_id,
        "xpack" : { "type" : "json" }
    },
    "trigger" : { "schedule" : { "interval" : interval } },
    "input" : {
        "search" : {
            "request" : {
            "search_type" : "query_then_fetch",
            "indices" : indices ,
            "types" : [ ],
            "body" : {
                "size" : 0,
                "query" : query,
                "aggregations" : aggs
            }
            }
        }
    },
    "condition" : {
        "compare" : { "ctx.payload.aggregations.num_device_by_ip.value" : { "gt" : 0 } }
    },
    "actions" : {
    "webhook_test" : {
        "webhook" : {
        "scheme" : "http",
        "host" : "54.208.72.130",
        "port" : 3009,
        "method" : "post",
        "path" : "/",
        "params" : { },
        "headers" : {
            "Content-Type" : "application/json"
        },
        "body" : body_webhook
        }
    }
    }
}
    
    return watcher