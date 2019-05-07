# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Last update: 07/05/2019
# Description: Procesar las alertas generadas & otras utilerias
#######################################################################################
import argparse, sys
from datetime import datetime
from elastic import *
#######################################################################################
def download_cmdb_elk(elk=None, q_filter = {}, nameFile = "cmdb_elk.yml", coding='utf-8'):
    list_datos = ["ip","cliente","sede","nombre_cluster","ip_group","categoria","modelo_equipo","marca_equipo"]
    array_filter = [ {"exists": {"field": "ip"}} ]
    
    if elk==None: elk=elasticsearch()
    if q_filter!={} : array_filter.append(q_filter)
    data_query = { #GET supra_data/_search
        "size": 1000,
        "_source": list_datos,
        "query": {
            "bool": {
            "must": array_filter
            }
        }
    }
    URL_API = "{0}/supra_data/_search".format(elk.get_url_elk())
    data_response = elk.req_get(URL_API, data = data_query)
    if len(data_response)<0:
        print("ERROR | {0} download_cmdb_elk | Failed to download data from elasticsearch.".format(datetime.utcnow().isoformat()))
    print_json(data_response)
    array_data = getelementfromjson(data_response, "hits.[hits]._source")
    
    fnew  = open(nameFile,"wb")
    for data_json in array_data:
        line = "\"{0}\"".format( data_json[list_datos[0]] )
        for i in range(1,len(list_datos)):
            field = list_datos[i]
            try:
                value = data_json[field]
            except:
                value = "*"
            finally:
                if i==1:
                    line = "{0} : {1}".format ( line, value )
                else:
                    line = "{0};{1}".format ( line, value )
        line = line+"\n"
        fnew.write(line.encode(coding))
    fnew.close()
    return array_data
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
def flush_index(name_index):
    #Limpia la data de un index sin eliminar el indice
    return
#######################################################################################
def block_write_index(name_index, write_block=False):
    # Si write_block=True, bloque <name_index> contro escritura
    elk = elasticsearch()
    URL_FULLPATH = "{0}/_settings".format( elk.get_url_elk() )
    elk.req_put(URL_FULLPATH, data={"index.blocks.write":write_block})
    return
#######################################################################################
def get_list_index(names_index,filter_idx_sys=True, show_properties="settings.index.blocks.write"):
    elk = elasticsearch()
    URL_FULLPATH = "{0}/{1}/_settings".format( elk.get_url_elk() , names_index)
    if names_index.find(".")==0: filter_idx_sys=False
    rpt_json = elk.req_get(URL_FULLPATH)
    list_idx = []
    print_json(rpt_json)
    for key in rpt_json:
        if key.find(".")!=0 and  filter_idx_sys:
            list_idx.append(key)
        if not filter_idx_sys:
            list_idx.append(key)
    print_list(list_idx, num=1)
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
#######################################################################################
def get_parametersCMD():
    command = value = client = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--command",help="Comando a ejecutar en la terminal [ ]")
    parser.add_argument("-v","--value",help="Comando a ejecutar en la terminal [ ]")
    parser.add_argument("-f","--client",help="Commando para filtar por cliente [ ]")
    args = parser.parse_args()

    if args.command: command = str(args.command)
    if args.value: value = str(args.value) 
    if args.client: client = str(args.client) 
    if( command==None):
        print("ERROR: Faltan parametros.")
        print("command\t [{0}]".format(command))
        sys.exit(0)
    if command=="update" and value!=None:
        print("INFO  | update {0}".format(value))
        if client !=None :
            q_filter = {"match": {"cliente": client}}
        else:
            q_filter = {}
        download_cmdb_elk(nameFile=value,q_filter=q_filter)
    elif command=="get_list_idx" and value!=None:
        get_list_index(value) #value=".*"
    else:
        print("ERROR | No se ejecuto ninguna accion.")
    return
#######################################################################################
if __name__ == "__main__":
    #block_write_index("syslog-alianza-write", write_block=True)
    #get_list_index(".*")
    get_parametersCMD()
    pass