# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Last update: 30/05/2019
# Description: Procesar las alertas generadas & otras utilerias
#######################################################################################
import argparse, sys
from datetime import datetime
from elastic import *
#######################################################################################
def bytesELK2json(data,codification='utf-8'):
    d_dict = {}
    #print(str(data))
    try:
       d_str = data.decode(codification)
       d_str = d_str.replace("false","False")
       d_str = d_str.replace("true","True")
       d_str = d_str.replace("null","None")
       d_dict = eval(d_str)
    except:
       print("[ERROR] type = %s ".format( type(data) ))
    finally:
       return d_dict
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
    #print_json(data_response)
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
                    line = "{0} : \"{1}".format ( line, value )
                else:
                    line = "{0};{1}".format ( line, value )
        line = line+"\"\n"
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
def download_watchers(elk=None):
    data_query = { #GET supra_data/_search
        "size": 1000,
        "query": {
            "match_all": {}
            }
        }
    
    URL_API = "{0}/.watches/_search".format(elk.get_url_elk())
    data_response = elk.req_get(URL_API, data = data_query)
    return
#######################################################################################
def download_incidencias(elk=None):
    if elk==None: elk = elasticsearch()
    data_query = {
        "size": 1000,
        "query": {
            "exists": { "field" : "incidencia_type"}
        },
        "aggs": {
            "incidencias_type":{
                "terms": {"field": "incidencia_type.keyword", "size": 100}
            }
        }
    }
    URL_API = "{0}/index_configuration/_search".format(elk.get_url_elk())
    try:
        data_response = elk.req_get(URL_API, data=data_query)
        list_incidencias = data_response["hits"]["hits"]
        save_yml({"list_incidencias": list_incidencias},nameFile="incidencias.yml")
    except:
        print("ERROR | download_incidencias ")
    finally:
        return
def get_incidencia(incidencia_type):
    #list_incidencias = []
    incidencias_json = loadYMLtoJSON("incidencias.yml")
    for data_json in incidencias_json["list_incidencias"]:
        if data_json["_source"]["incidencia_type"] == incidencia_type:
            return data_json["_source"]
    return {}
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
"""
#######################################################################################
def download_and_update_dictionary_cmdb(elk=None):
    if elk==None: elk = elasticsearch()
    dict_cmdb_ip = {}
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
    
def get_list_index(names_index, filter_idx_sys=True, path = None, show_null_values=False):
    elk = elasticsearch()
    if names_index.find(".")==0: filter_idx_sys=False
    URL_FULLPATH = "{0}/{1}/_settings".format( elk.get_url_elk() , names_index)
    data_json = elk.req_get(URL_FULLPATH)
    #print_json(data_json)
    idx_ini = 0
    if path!=None:
        idx_end = path.find(".")
    else:
        idx_end = 0
    list_elements=[]
    while idx_end >=0 :
        keylist = sorted(data_json.keys())
        if path==None or len(path)==0:
            for key in keylist:
                list_elements.append(key)
            break
        else:
            elem_path = path[idx_ini: idx_end]
            path = path[idx_end+1:]
            if (elem_path=="*"):
                for key in keylist:
                    new_path = "{0}.{1}".format(key,path)
                    tmp_data = getelementfromjson(data_json,new_path)
                    if len(tmp_data) == 1:
                        list_elements.append( { 'key': key, 'val' : tmp_data[0] } )
                    elif (not show_null_values and len(tmp_data)>1):
                        list_elements.append( { 'key': key, 'val' : tmp_data } )
                    elif (show_null_values and len(tmp_data)==0):
                        list_elements.append( { 'key': key, 'val' : ""} )
            idx_end = path.find(".")
    #print_json(list_elements)
    return list_elements
#######################################################################################
def get_index_by_allocation(names_index, filter_idx_sys=True, path="*.settings.index.routing.allocation.include.instance_configuration"):
    list_index = get_list_index(names_index, filter_idx_sys=filter_idx_sys, path=path, show_null_values=True)
    list_index_hot = []
    list_index_warm = []
    for index in list_index:
        try:
            value = index['val']
        except:
            value = ""
        finally:
            if value.find("highstorage")>0:
                list_index_warm.append(index)
            elif value.find("highio")>0:
                list_index_hot.append(index)
            else:
                list_index_hot.append(index)
    #print_json(new_list_index_hot)
    data_json = {
        'hot': getelementfromjson( {"array": list_index_hot}, "[array].key"),
        'warm': getelementfromjson( {"array": list_index_warm}, "[array].key")
    }
    print_json(data_json)
    return data_json
"""
#######################################################################################
def get_resume_status_nodes():
    elk = elasticsearch()
    URL_FULLPATH = "{0}/_nodes/stats".format( elk.get_url_elk() )
    rpt_json = elk.req_get(URL_FULLPATH)
    #print_json(rpt_json)
    #save_yml(rpt_json,nameFile="nodes_elk.yml")
    list_nodes = []
    path = "nodes.*.{attributes.instance_configuration,fs.total.{free_in_bytes,total_in_bytes}}"
    
    for node in rpt_json['nodes']:
        list_nodes.append(node)
    print_list(list_nodes)
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
def download_watches(filter={"match_all":{}}, elk=elasticsearch(), nameFile="watches.yml"):
    list_watches = []
    query = {
        "size": 10000,
        "query": filter
        #,"_source": ["_id"]
    }
    URL = "{0}/.watches/_search".format( elk.get_url_elk() )
    rpt_json = elk.req_get(URL, data=query)
    list_watches = getelementfromjson(rpt_json, "hits.[hits]")[0]
    rpt_json =[]
    for watch in list_watches:
        _id = watch['_id']
        _source = watch['_source']
        _trigger = watch['_source']['trigger']
        _input = watch['_source']['input']
        _condition = watch['_source']['condition']
        _actions = watch['_source']['actions']
        _metadata = watch['_source']['metadata']
        #_status = watch['_source']['status']['state']['active']
        tmp_json = {
            _id: {
                "metadata": _metadata,
                "trigger": _trigger,
                "input": _input,
                "condition": _condition,
                "actions": _actions
            }
        }
        rpt_json.append(tmp_json)
    if len(rpt_json)>0:
        #print_json(list_watches)
        print("{1}| download_watches| INFO | downloading <{0}>".format(nameFile, datetime.utcnow().isoformat()))
        get_list_watches()
        if nameFile!=None:
            save_yml({"watches": rpt_json}, nameFile)
    else:
        print("{1}| download_watches| ERROR | downloading <{0}>".format(nameFile, datetime.utcnow().isoformat()))
    return rpt_json
#######################################################################################
def build_query_filter(index, terms=[], size=0, sort=["@timestamp","desc"]):
    list_match = []
    for item in terms:
        list_match.append({"match": item} )
    data_query = {
        "size": size,
        "sort": [{sort[0]: {"order": sort[1]}}],
        "query": {"bool": {"must": list_match}},
        "aggs": {
            "ip": {
                "terms": {"field": "cmdb.reporting_ip","size": 1000},
                    "aggs": {
                        "last_status": {
                            "top_hits": {
                                "size": 1,
                                "sort": [{"@timestamp": {"order": "desc"}}],
                                "_source": ["cmdb","monitor"]
                            }
                        }
                    }
                }
            }
    }
    #print_json(data_query)
    return data_query
#######################################################################################
def get_data_by_filter(index , terms=[], size=0, elk=elasticsearch()):
    rpt_json = {}
    URL = "{0}/{1}/_search".format( elk.get_url_elk() , index )
    rpt_json = elk.req_get(URL, data=build_query_filter(index, terms=terms, size=size))
    return rpt_json
#######################################################################################
def get_list_watches(filter={"match_all": {}}, elk=elasticsearch()):
    list_watches = []
    query = {
        "size": 10000,
        "query": filter,
        "_source": ["_id"]
    }
    
    URL = "{0}/.watches/_search".format( elk.get_url_elk() )
    rpt_json = elk.req_get(URL, data=query)
    #print_json(rpt_json)
    list_watches = getelementfromjson(rpt_json, "hits.[hits]._id")
    print_list(list_watches , num=1)
    return list_watches
#######################################################################################
def get_parametersCMD():
    command = value = client = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--command",help="Comando a ejecutar en la terminal [update, get_list_idx, download_watches ]")
    parser.add_argument("-v","--value",help="Comando a ejecutar en la terminal [nameFile.jml ]")
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
    elif command=="download_watches":
        download_watches(nameFile=value)
    elif command=="download_incidencias":
        download_incidencias()
    else:
        print("ERROR | No se ejecuto ninguna accion.")
    return
#######################################################################################
if __name__ == "__main__":
    print("[INI] utils_elk.py")
    get_parametersCMD()
    #block_write_index("syslog-alianza-write", write_block=True)
    #get_resume_status_nodes()
    #get_list_index("*-write")
    #get_list_watches()
    #download_watches()
    #get_list_index("*-group*")
    #download_incidencias()
    #get_incidencia("network_device_status")
    pass