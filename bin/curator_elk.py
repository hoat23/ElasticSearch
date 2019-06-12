# coding: utf-8
# Developer: Deiner Zapata Silva.
# Date: 02/14/2019
# Last update: 09/06/2019
# Description: Procesar las alertas generadas & otras utilerias
#######################################################################################
import argparse
import sys
from logging_advance import *
from datetime import datetime
from utils import *
from utils_elk import *
#from flatten_json import flatten
from elastic import *
#######################################################################################
dict_real_name = {"hot": "aws.data.highio.i3", "warm": "aws.data.highstorage.d2", "ml":"aws.ml.m5", "m":"aws.master.r4"}
#######################################################################################
log = logging_advance(fullpath=__file__,send_elk=True)
#######################################################################################
def execute_readonly(index, value = True):
    flagExecuted=False
    elk = elasticsearch()
    rpt_json = {}
    try: 
        URL_API = "{0}/{1}/_settings".format(elk.get_url_elk(), index )
        data_query = {"index.blocks.write": value}
        rpt_json = elk.req_put( URL_API , data=data_query )
        flagExecuted = True
    except:
        log.print_error("flagExecute={0}", name_function="execute_readonly", data_json=rpt_json)
    finally:
        log.print_info("{0:23s}| flagExecute={1}".format(index , flagExecuted), name_function="execute_readonly")
        return flagExecuted
#######################################################################################
def execute_forcemerge(index,cont=0):
    #only executed if index is readonly
    flagExecuted=False
    elk = elasticsearch()
    rpt_json = {}
    if cont>3: return False
    try:
        URL_API ="{0}/{1}/_settings".format( elk.get_url_elk(), index)
        rpt_json =  elk.req_get( URL_API )
        path = "{0}.settings.index.blocks.write".format(index)
        blocks_write = getelementfromjson( rpt_json ,path)
        if len(blocks_write)>0:
            blocks_write=blocks_write[0]
        else:
            blocks_write="false"
        if blocks_write=="true" or blocks_write==True:
            URL_API = "{0}/_forcemerge".format( elk.get_url_elk() )
            rpt_json = elk.req_post( URL_API , data = {})
            flagExecuted = True
        else:
            cont = cont+1
            log.print_info("Executing read_only cont={0}".format(cont), name_function="execute_forcemerge", data_json=rpt_json)
            execute_readonly(index)
            flagExecuted = execute_forcemerge(index, cont=cont)
            return flagExecuted
    except:
        log.print_debug("Exception cached.", name_function="execute_forcemerge", data_json=rpt_json)
    finally:
        log.print_info("Executed idx={0} flagExecute={1}".format(index, flagExecuted), name_function="execute_forcemerge", data_json=rpt_json)
    return flagExecuted
#######################################################################################
def execute_index_write_in_hot(index="*-write"):
    rpt = execute_migration_nodes([index],to_node="hot")
    log.print_info("HOT | flagExecute={0}".format(rpt), name_function="execute_index_write_in_hot")
    return rpt
#######################################################################################
def execute_migration_nodes(list_index, to_node=""):
    flagExecuted=False
    #PUT *-group*-write/_settings
    if len(list_index)==0: return False
    elk = elasticsearch()
    rpt_json = {}
    try:
        real_node_name = dict_real_name[to_node]
        for index in list_index:
            URL_API = "{0}/{1}/_settings".format(elk.get_url_elk(), index )
            data_query = {"index.routing.allocation.include.instance_configuration": real_node_name}
            rpt_json = elk.req_put( URL_API, data=data_query )
            flagExecuted = True
    except:
        log.print_info("{1} | flagExecute={0}".format(flagExecuted, list_index), name_function="execute_migration_nodes")
    finally:
        #print_json(rpt_json)
        return flagExecuted
#######################################################################################
def order_idx_in_hot_warm(types_of_index=[], num_idx_in_hot=1, flag_remove_write_from_hot=False):
    # {type_of_index}-{groups_by_index}-000000
    dict_idx = { }
    for idx_type in types_of_index:
        idx_pattern = "{0}*".format(idx_type)
        list_idx = get_simple_list_index(idx_pattern, sort_reverse=True)
        list_idx_hot = get_simple_list_index(idx_pattern + "-write")
        #By default idx write in Hot Node
        if flag_remove_write_from_hot: list_idx.remove( list_idx_hot[0] ) 
        dict_idx.update( 
            {idx_type : {
                "hot" : list_idx[:num_idx_in_hot],
                "warm": list_idx[num_idx_in_hot:],
                "write": list_idx_hot
                }
            })
    #print_json(dict_idx)
    return dict_idx
#######################################################################################
def police_index_in_hot(types_of_index=[], num_idx_in_hot=2, exe_idx_write_in_hot=True):
    flagExecute = True
    types_of_index=[
        "syslog-group01",
        "syslog-group02",
        "syslog-group03",
        "syslog-group04",
        "syslog-group05",
        "heartbeat-group01",
        "health-group01",
        "snmp-group01"]
    dict_idx_hot_warm = order_idx_in_hot_warm(types_of_index=types_of_index, num_idx_in_hot=num_idx_in_hot)
    for idx_type in  types_of_index:
        settings_on_idx = dict_idx_hot_warm[idx_type]
        list_idx_hot = settings_on_idx['hot']
        list_idx_warm = settings_on_idx['warm']
        flagExecuteHot = execute_migration_nodes(list_idx_hot,"hot")
        flagExecuteWarm = execute_migration_nodes(list_idx_warm,"warm")
        log.print_info("{2:23s}| flagExecuteHot={1:5s} | flagExecuteWarm={0:5s}".format( str(flagExecuteWarm), str(flagExecuteHot) , idx_type) , name_function="police_index_in_hot")
    #print_json(dict_idx_hot_warm)
    if (exe_idx_write_in_hot):
        execute_index_write_in_hot(index="*group*-write")
    return flagExecute
#######################################################################################
def police_forcemerge(idx_pattern="*-group*",type_node="hot"):
    list_idx = get_index_by_allocation(idx_pattern,filter_by_allocation=type_node)
    list_idx_write = get_simple_list_index(idx_pattern+"-write")
    #print_json(list_idx)
    #print_json(list_idx_write)
    for index_write in list_idx_write:
        if index_write in list_idx:
            list_idx.remove( index_write )
    log.print_info("type_node={0:4s} | num_idx={1}".format(type_node, len(list_idx)),name_function="police_forcemerge", data_json={"buckets": list_idx})
    for index in list_idx:
        execute_forcemerge(index)
    return
#######################################################################################
def police_space_over_percentage_by_node(value_usage_disk, type_node, flagExecute = False):
    lista_data_nodes = get_resume_space_nodes(filter_type_node=type_node)
    #print_json(lista_data_nodes)
    max_value = 0
    for one_node in lista_data_nodes:
        usage_in_percentage = one_node['usage_in_percentage']
        if (usage_in_percentage > max_value): max_value = usage_in_percentage
        if (usage_in_percentage>=value_usage_disk):
            flagExecute=True
            break
    log.print_info("{0:.2f}% |{1:5s}| max_value={2:.2f} flagExecute={3}".format(value_usage_disk, type_node.upper(), max_value ,flagExecute), name_function="police_space_over_percentage_by_node")
    if flagExecute:
        index = "*group*"
        data_json = get_index_by_allocation(index,filter_by_allocation=type_node)
        #"acknowledged": true
        log.print_info("", name_function="police_space_over_percentage_by_node", data_json=data_json)
    return flagExecute
#######################################################################################
def get_parametersCMD_curator_elk():
    command = value = index = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--command",help="Comando a ejecutar en la terminal [update, get_list_idx, download_watches, update_dict_monitoring ]")
    parser.add_argument("-v","--value",help="Comando a ejecutar en la terminal [nameFile.jml ]")
    parser.add_argument("-i","--index",help="Commando para especificar el indice (soporta wildcards)")
    args = parser.parse_args()

    if args.command: command = str(args.command)
    if args.value: value = str(args.value) 
    if args.index: index = str(args.index)
    if( command==None):
        print("ERROR: Faltan parametros.")
        print("command\t [{0}]".format(command))
        sys.exit(0)
    elif command=="exe_idx_write_in_hot" and index!=None: # index=*group*-write 
        #python curator_elk.py -c exe_idx_write_in_hot --index *group*-write
        execute_index_write_in_hot(index=index)
    elif command=="exe_policy_idx_in_hot_warm":
        #python curator_elk.py -c exe_policy_idx_in_hot_warm
        police_index_in_hot()
    elif command=="exe_read_only" and index!=None:
        #python curator_elk.py -c exe_read_only --index syslog-group05-000001
        if value!=None:
            execute_readonly(index, value=value)
        else:
            execute_readonly(index, value=True)
    elif command=="exe_forcemerge" and index!=None:
        #python curator_elk.py -c exe_forcemerge --index syslog-group05-000001
        execute_forcemerge(index)
    elif command=="policy_hot_space_over" and value!=None:
        #python curator_elk.py -c policy_hot_space_over -v 75.0
        police_space_over_percentage_by_node(float(value),"hot")
    elif command=="policy_warm_space_over" and value!=None:
        #python curator_elk.py -c policy_warm_space_over -v 75.0
        police_space_over_percentage_by_node(float(value),"warm")
    elif command=="police_forcemerge":
        #python curator_elk.py -c police_forcemerge
        police_forcemerge()
    else:
        print("ERROR | No se ejecuto ninguna accion.")
    return
#######################################################################################
if __name__ == "__main__":
    #log.print_info("Iniciando Curator")
    get_parametersCMD_curator_elk()
    #police_index_in_hot()
    #police_space_over_percentage_by_node(75.0,"hot")
    #police_forcemerge()
    #police_space_over_percentage_by_node(75.0,"warm")
    #list_idx = [    "syslog-group01-000027", "syslog-group01-000028"]
    #execute_migration_nodes(list_idx, to_node="warm")
    pass