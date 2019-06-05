# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Last update: 31/05/2019
# Description: Procesar las alertas generadas & otras utilerias
#######################################################################################
import argparse, sys
from datetime import datetime
from elastic import *
from utils import *
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
       print("[ERROR] type = {0} ".format( type(data) ))
    finally:
       return d_dict
#######################################################################################
def build_json_cmdb_elk(data_json):
    bucket_list = []
    for clientes in data_json['aggregations']['cliente']['buckets']:
        cliente =  clientes['key']
        list_datos_by_client = []
        for ip_s in clientes['groupIP']['buckets']:
            ip = ip_s['key']
            to_monitoring = []
            protocolos_json = {}
            list_protocolos = []
            for protocolos in ip_s['groupProtocolo']['buckets']:
                protocolo = protocolos['key']
                if len(protocolo)==0 or protocolo==None: 
                    print("[WARN ] build_json_cmdb_elk | ERROR <field:protocolo>[ ip:{0:16s} client:{2:20s} protocolo: {1}]".format(ip, protocolo, cliente))
                    protocolo="ping"
                list_protocolos.append(protocolo)
                list_puertos = []
                for puertos in protocolos['groupPort']['buckets']:
                    puerto = puertos['key']
                    dif_fields = puertos['tops']['hits']['hits'][0]['_source']
                    if (len(puerto)<=0): puerto = "default"
                    list_puertos.append( { 'value' : puerto, "cmdb" : dif_fields})
                if (len(list_puertos)>0):
                    protocolos_json.update( { protocolo: list_puertos } )
                to_monitoring.append( protocolo )
            #print(" [{0:25s}] \t {1:15s} {2}".format(cliente, ip, ",".join(list_protocolos)))
            data_by_device = {
                "ip": ip,
                "protocolo": protocolos_json,
                "to_monitoring": to_monitoring
            }
            list_datos_by_client.append(data_by_device)
        bucket_list.append({"key": cliente, "buckets": list_datos_by_client})
    
    return bucket_list
#######################################################################################
def build_query_monitoring_by_client(client ,elk=elasticsearch(), index="supra_data", list_dif_fields=[], add_on_doc_in_groupIP=False, list_common_fields=["cliente","sede","nombre_cluster","ip_group","categoria","modelo_equipo","marca_equipo"]):
    ip_priv = {
    "bool": {
        "should": [
            {"range": {"ip": {"gte": "192.168.0.0","lte": "192.168.255.255"}}},
            {"range": {"ip": {"gte": "172.16.0.0","lte": "172.31.255.255"}}},
            {"range": {"ip": {"gte": "10.0.0.0","lte": "10.255.255.255"}}}]}
    }
    data_query = {#GET supra_data/_search
    "size": 0,
    "query": {
        "bool": {
            "must": [],
            "must_not": []
        }
    }
    }
    data_aggs={
        "aggs": {
        "cliente": {"terms": {"field": "cliente","size": 1000},
            "aggs": {
                "groupIP": {"terms": {"field": "ip","size": 1000},
                "aggs": {
                    "groupProtocolo": {"terms": {"field": "protocolo","size": 1000
                    },
                    "aggs": {
                        "groupPort": {"terms": {"field": "puerto","size": 1000
                        },
                        "aggs": {
                            "tops": {"top_hits": {"size": 1,"sort": [{"@timestamp": {"order": "desc"}}] }
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
        }
    }}

    if len(list_dif_fields)>0:
        data_aggs["aggs"]["cliente"]["aggs"]["groupIP"]["aggs"]["groupProtocolo"]["aggs"]["groupPort"]["aggs"]["tops"]["top_hits"].update( {"_source": list_dif_fields })
    
    if add_on_doc_in_groupIP:
        aux_query = {
            "one_doc": {
                "top_hits": {
                    "size": 1,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "_source": list_common_fields
                }
            }
        }
        data_aggs["aggs"]["cliente"]["aggs"]["groupIP"]["aggs"].update( aux_query )
    #filter by client
    if (client=="AWS"): 
        ip_private = False
    else: 
        data_query['query']['bool']['must'].append( {"match": {"cliente": client}} )
        ip_private = True
    
    #filter by exists fields
    data_query['query']['bool']['must'].append( {"exists": {"field":"ip"}} )
    data_query['query']['bool']['must'].append( {"exists": {"field":"protocolo"}} )
    #filter by private ip
    if (ip_private):
        data_query['query']['bool']['must'].append( ip_priv )
    else:
        data_query['query']['bool']['must_not'].append( ip_priv )
    data_query.update( data_aggs)
    return data_query
#######################################################################################
def update_dict_monitoring_by_client(client ,elk=elasticsearch(), index="supra_data", list_dif_fields=["tipo_ip_equipo","ip_group"]):
    data_query = build_query_monitoring_by_client(client, elk=elk, index=index, list_dif_fields=list_dif_fields)
    #Doing the query to elk.
    URL_API = "{0}/{1}/_search".format(elk.get_url_elk(), index)
    rpt_json = elk.req_get(URL_API, data=data_query)
    data_procesed = build_json_cmdb_elk(rpt_json)
    #save_yml(data_procesed,"cmdb_testing.yml")

    index_config = "index_configuration"
    doc_id = "dict_monitoring_"+client.lower().replace(" ","_")
    rpt_json = elk.req_get("{0}/{1}/_doc/{2}".format(elk.get_url_elk(), index_config, doc_id))
    data_to_update = { 
        "key": "dict_"+client.lower(), 
        "buckets": data_procesed, 
        "last_update": "{0}".format( datetime.utcnow().isoformat()) 
        } 
    URL_FULLPATH = "{0}/{1}/_doc/{2}".format(elk.get_url_elk(), index_config, doc_id)
    if "found" in rpt_json:
        if rpt_json['found']=="false": 
            URL_FULLPATH = "{0}/{1}/_update/{2}?pretty".format(elk.get_url_elk(), index_config, doc_id)
    print("[INFO] update_dict_monitoring_by_client [{0}|_doc|{1}]".format(index_config, doc_id))
    print(URL_FULLPATH)
    rpt_json = elk.req_post(URL_FULLPATH, data=data_to_update )
    if "status" in rpt_json:
        if rpt_json["status"]==400:
            #print_json(data_to_update)
            print_json(rpt_json)
            #save_yml(data_to_update, nameFile="debug.yml")
    return 
#######################################################################################
def download_cmdb_elk(client,elk=None, index="supra_data", nameFile = "cmdb_elk.yml", coding='utf-8'):
    build_query_monitoring_by_client("AWS")
    array_data = []
    list_common_fields =["cliente","sede","nombre_cluster","ip_group","categoria","modelo_equipo","marca_equipo"]
    if elk==None: elk = elasticsearch()
    URL_API = "{0}/{1}/_search".format(elk.get_url_elk(), index)
    data_query = build_query_monitoring_by_client(client, elk=elk, index=index, list_dif_fields=["tipo_ip_equipo","ip_group"], add_on_doc_in_groupIP=True, list_common_fields=list_common_fields)
    data_json = elk.req_get( URL_API, data=data_query )
    fnew  = open(nameFile,"wb")
    for clientes in data_json['aggregations']['cliente']['buckets']:
        cliente =  clientes['key']
        list_datos_by_ip = []
        for ip_s in clientes['groupIP']['buckets']:
            ip = ip_s['key']
            #print_json(data_response)
            #common_fields = getelementfromjson(ip_s, "one_doc.hits.[hits]._source")
            common_fields = ip_s['one_doc']['hits']['hits'][0]["_source"]
            #save_yml(ip, nameFile="debug.yml")
            list_fields = []
            for field in list_common_fields:
                try:
                    value = common_fields[field]
                    if value==None: value = "*"
                except:
                    value = "*"
                finally:
                    list_fields.append(value)
            if len(list_fields)>0:
                str_fields = ",".join(list_fields)
                line = " {0:23s} : \"{1}\"\n".format(ip, str_fields) 
                fnew.write(line.encode(coding))
    fnew.close()
    
    #save_yml(data_json, nameFile = "debug.yml")
    return array_data
#######################################################################################
def download_configuration_from_elk(elk):
    dict_client_ip = {}
    logstash = {}
    data_query = { #GET index_configuration/_search?filter_path=hits.hits._source.logstash
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "logstash"}}
                ]
            }
        }
    }
    
    data_response = elk.req_get(elk.get_url_elk()+"/index_configuration/_search?filter_path=hits.hits._source",data=data_query)['hits']['hits'][0]['_source']
    if len(data_response)<0:
        print("ERROR | {0} download_configuration | Failed to download data from elasticsearch.".format(datetime.utcnow().isoformat()))

    if 'logstash' in data_response:
        logstash = data_response['logstash']
    else:
        print("ERROR | {0} download_configuration | 'logstash' key don't exists in json response.".format(datetime.utcnow().isoformat()))
    
    return logstash
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
def get_list_clientes(elk =elasticsearch(), index="supra_data"):
    data_query = {
        "size": 0, 
        "query": {
            "bool": {"must": [{"exists": {"field": "cliente"}}]}
        },
        "aggs": {
            "cliente": {"terms": {"field": "cliente","size": 1000}}
        }
    }
    URL_FULLPATH = "{0}/{1}/_search".format( elk.get_url_elk() , index )
    rpt_json = elk.req_get( URL_FULLPATH, data = data_query )
    list_clients = getelementfromjson(rpt_json,"aggregations.cliente.[buckets].key")
    return list_clients
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
def get_one_field_in_document(index="index_configuration",one_field="dict_client_ip", elk= elasticsearch()):
    #Using only one exists a field only in one doc
    data_query = {
        "query": {
            "bool": {
                "must": [{"exists": {"field": one_field}}]
            }
        },
        "size": 1
    }
    URL_API = "{0}/{1}/_search".format(elk.get_url_elk(), index )
    rpt_json = elk.req_get(URL_API, data=data_query)
    print_json(rpt_json)
    return rpt_json
def update_fields_in_document(index="index_configuration",one_field="dict_client_ip", elk=elasticsearch()):
    """
    POST {index}/_update_by_query?refresh
    {
        "script": {
            "inline": "
            ctx._source['type_device'] = 'firewall';
            ctx._source['client'] = 'tasa';
            "
        }
    }
    """
    rpt_bool = False
    list_docs = get_one_field_in_document(index, one_field, elk)
    print_json(list_docs)
    return rpt_bool
#######################################################################################
def get_parametersCMD():
    command = value = client = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--command",help="Comando a ejecutar en la terminal [update, get_list_idx, download_watches, update_dict_monitoring ]")
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
    if command=="download_cmdb_elk" and client!=None:
        print("INFO  | cmdb_elk [{0}]".format(client))
        download_cmdb_elk(client)
    elif command=="get_list_idx" and value!=None:
        get_list_index(value) #value=".*"
    elif command=="download_watches":
        download_watches(nameFile=value)
    elif command=="download_incidencias":
        download_incidencias()
    elif command=="update_dict_monitoring" and client!=None:
        update_dict_monitoring_by_client(client)    
    else:
        print("ERROR | No se ejecuto ninguna accion.")
    return
#######################################################################################
if __name__ == "__main__":
    print("[INI] utils_elk.py")
    #update_dict_monitoring_by_client("PROMPERU")
    #update_fields_in_document()
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