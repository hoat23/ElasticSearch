import requests
from bs4 import BeautifulSoup
import yaml #pyyaml
from utils import save_yml, print_json, loadCSVtoJSON, renameKeys, send_json
from elastic import *
import json, sys, time, datetime
#######################################################################################
global version_json_mcaffe
#######################################################################################
def get_version_mcaffe(nameFile='dat_releases.yml', url='https://www.mcafee.com/enterprise/en-us/downloads/security-updates.html'):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    #Scraping data and saving data in a file
    releases = dict()
    for table in soup.find_all('table'):
        data = []
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        release = dict()
        release['file_name'] = data[1][0]
        release['platform'] = data[1][1]
        release['release_version'] = int(data[1][3])
        release['release_date'] = data[1][4]
        if('V3' in release['file_name']):
            release['version'] = 'AMC'
        else:
            release['version'] = 'DAT'

        if(not release['platform'] == 'Linux'):
            releases[release['version']] = release #json.dumps(release)
            #releases[release['version']] = release
    save_yml(releases, nameFile = nameFile)
    return releases
#######################################################################################
def rename_data(data_json):
    new_data_json = {}
    dict_fiels_to_rename = {
        "\u00daltima comunicaci\u00f3n" : "timestamp",
        "Última comunicaci\u00f3n" : "timestamp",
        "última comunicaci\u00f3n" : "timestamp",
        "\ufeffNombre de sistema" : "hostame",
        "Nombre de sistema" : "hostame",
        "Tipo de SO" : "sistema_operativo",
        "Versi\u00f3n de producto (Agent)" : "vers_producto_agente",
        "Versión de producto (Agent)" : "vers_producto_agente",
        "Versi\u00f3n de producto (Endpoint Security Threat Prevention)" : "version_producto_EST",
        "Versión de producto (Endpoint Security Threat Prevention)" : "version_producto_EST",
        "Tipo de Producto" : "tipo_producto",
        "Estatus_Version_Producto (VSE/EST)" : "status_vers_producto_VSE_EST",
        "Versi\u00f3n de producto (VirusScan Enterprise)" : "version_producto_VSE",
        "Versión de producto (VirusScan Enterprise)" : "version_producto_VSE",
        "Versi\u00f3n de DAT (VirusScan Enterprise)" : "version_DAT",
        "Versión de DAT (VirusScan Enterprise)" : "version_DAT",
        "Versi\u00f3n de AMCore Content" : "version_AMC",
        "Versión de AMCore Content" : "version_AMC",
        "estatus_DAT_AMC" : "status_DAT_AMC",
        "Estatus_Final" : "status_Final",
        "Version_DAT_AMC_Cruce" : "version_Final_DAT_AMC",
        "Estatus_Version_Producto_Agente": "status_vers_producto_agente",
        "Estatus_Version_Producto (VSE/EST)": "status_vers_producto_VSE_EST",
        "Tipo de Producto" : "tipo_producto",
        "estatus_DAT_AMC" : "status_DAT_AMC",
    }
    list_data_json=[]
    for aux_json in data_json:
        temp_json = renameKeys(aux_json, dict_fiels_to_rename)
        list_data_json.append(temp_json)
        #print_json(temp_json)
    return list_data_json
#######################################################################################
def convert_date(string_data):
    new_data = ""
    list_data = string_data.split("/")
    new_data = list_data[1] + "/" + list_data[0] + "/20" + list_data[2]
    return new_data
#######################################################################################
def diff_days(day_2, day_1, formato = "%m/%d/%Y"):
    curr_date_parsed = datetime.datetime.strptime(str(day_2), formato)
    new_date_parsed = datetime.datetime.strptime(str(day_1), formato)
    diff_date = (curr_date_parsed - new_date_parsed).days
    return diff_date
#######################################################################################
def get_name_month_anio(date_string):
    months = [
        "Ene",
        "Feb",
        "Marz",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic"
    ]
    anio = date_string.split()[0].split("/")[2] # dd/mm/YY
    month = date_string.split()[0].split("/")[1] # dd/mm/YY
    num_month = int(month)

    return months[num_month-1] + " " + anio

#######################################################################################
def recalculateVersion(version_json, release_date_to_calculate):
    # release_date_to_calculate = "mm/dd/YYYY"
    new_version_json = {}
    #print("date " + release_date_to_calculate)
    #print_json(version_json)

    v2_json = version_json["DAT"]
    v3_json = version_json["AMC"]

    v2_json.update({"release_version" : v2_json["release_version"] - diff_days(version_json["DAT"]["release_date"], release_date_to_calculate)})
    v2_json.update({"release_date" : release_date_to_calculate})
    v3_json.update({"release_version" : v3_json["release_version"] - diff_days(version_json["AMC"]["release_date"], release_date_to_calculate)})
    v3_json.update({"release_date" : release_date_to_calculate})

    new_version_json = {
        "DAT" : v2_json,
        "AMC" : v3_json
    }
    
    #print_json(new_version_json)
    
    return new_version_json
#######################################################################################
def calc_status_vers_product_agent(list_json_old_data):
    name_field = "status_vers_producto_agente"
    cont = 0 
    list_json_new_data = []
    for data_json in list_json_old_data:
        #print("Processing data {0}".format(cont))
        #print_json(data_json)
        vers_producto_agente = data_json["vers_producto_agente"]
        if ( len(vers_producto_agente)>0 ):
            value_field = "Actualizado"
        else:
            value_field = "No actualizado"
        #print("calc_status_vers_product_agent  [{0}]".format(value_field) )
        data_json.update( {name_field : value_field} )
        list_json_new_data.append(data_json)
        cont = cont + 1
        #time.sleep(2)
    return list_json_new_data
#######################################################################################
def calc_tipo_product(list_json_old_data):
    name_field = "tipo_producto"
    cont = 0
    list_json_new_data = []
    for data_json in list_json_old_data:
        #print("calc_tipo_producto -> {0}".format(cont))
        version_producto_VSE = data_json["version_producto_VSE"]
        version_producto_EST = data_json["version_producto_EST"]
        #print_json(data_json)
        value_field = "VSE"
        if(len(version_producto_VSE)>0 and len(version_producto_EST)==0):
            value_field = "VSE"
        if(len(version_producto_VSE)==0 and len(version_producto_EST)>0):
            value_field = "EST"

        data_json.update(  {name_field : value_field})
        list_json_new_data.append(data_json)
        cont = cont + 1 
        #time.sleep(1)
    return list_json_new_data
#######################################################################################
def calc_status_vers_VST_EST(list_json_old_data):
    name_field = "status_vers_producto_VSE_EST"
    cont = 0
    list_json_new_data = []
    for data_json in list_json_old_data:
        #print("calc_status_vers_VST_EST -> {0}".format(cont))
        version_producto_VSE = data_json["version_producto_VSE"]
        version_producto_EST = data_json["version_producto_EST"]
        #print_json(data_json)
        
        if(len(version_producto_VSE)==0 and len(version_producto_EST)==0):
            value_field = "No actualizado"
        else:
            value_field = "Actualizado"
        data_json.update(  {name_field : value_field})
        list_json_new_data.append(data_json)
        cont = cont + 1 
        #time.sleep(1)
    return list_json_new_data
#######################################################################################
def calc_status_data_amc(list_json_old_data):
    global version_json_mcaffe
    name_field = "status_DAT_AMC"
    cont = 0
    list_json_new_data = []
    for data_json in list_json_old_data:
        #print("calc_status_data_amc -> {0}".format(cont))
        #print_json(data_json)
        tipo_producto = data_json["tipo_producto"]
        timestamp = data_json["timestamp"]
        version_json_mcaffe_aux =  recalculateVersion(version_json_mcaffe,convert_date(timestamp.split()[0]))
        if (tipo_producto=="VSE"):
            version = (data_json["version_DAT"])
            version_mcaffe = version_json_mcaffe_aux["DAT"]["release_version"]
        else:
            version = (data_json["version_AMC"])
            version_mcaffe = version_json_mcaffe_aux["AMC"]["release_version"]
        #print("\t version = {0} | {1}     onlyDate(timestamp) = ".format(version, version_mcaffe))
        
        if(len(version)==0):
            value_field = "No actualizado"
        elif(version_mcaffe-5.0<=float(version)):
            value_field = "Actualizado"
        else:
            value_field = "No actualizado"
        
        data_json.update(  {name_field : value_field,  "Version_DAT_AMC_Cruce": version_mcaffe})
        #print_json(data_json)
        list_json_new_data.append(data_json)
        cont = cont + 1 
        #sys.exit(0)
        #input("Press any key...")
        
    return list_json_new_data
#######################################################################################
def calc_status_final(list_json_old_data):
    name_field = "status_final"
    cont = 0
    list_json_new_data = []
    for data_json in list_json_old_data:
        status_DAT_AMC = data_json["status_DAT_AMC"]
        status_vers_producto_VSE_EST = data_json["status_vers_producto_VSE_EST"]
        status_vers_producto_agente = data_json["status_vers_producto_agente"]
        if( status_DAT_AMC=="Actualizado" and status_vers_producto_agente=="Actualizado" and status_vers_producto_VSE_EST=="Actualizado"):
            value_field = "Actualizado"
        else:
            value_field = "No actualizado"
        data_json.update(  {name_field : value_field, "mes" : get_name_month_anio(data_json["timestamp"])})
        #print_json(data_json)
        list_json_new_data.append(data_json)
        cont = cont + 1 
        
    return list_json_new_data
#######################################################################################
def process_data(list_json_old_data):
    list_json_new_data  = {}
    list_json_new_data = calc_status_vers_product_agent(list_json_old_data)
    #print_json(list_json_new_data)
    list_json_new_data = calc_tipo_product(list_json_new_data)
    #print_json(list_json_new_data)
    list_json_new_data = calc_status_vers_VST_EST(list_json_new_data)
    #print_json(list_json_new_data)
    list_json_new_data = calc_status_data_amc(list_json_new_data)
    #print_json(list_json_new_data)
    list_json_new_data = calc_status_final(list_json_new_data)
    print_json(list_json_new_data)
    return list_json_new_data
#######################################################################################
def send_to_elk(list_data_to_up_bulk):
    elk = elasticsearch()
    header_json={"index":{"_index":"repsol","_type":"_doc"}}
    elk.post_bulk(list_data_to_up_bulk,header_json=header_json)
    return
#######################################################################################
if __name__ == "__main__":
    global version_json_mcaffe
    print("Descarga de las versiones de MacAfee . . . ")
    print("Downloading actual version from McAffe . . . ")
    version_json_mcaffe = get_version_mcaffe()
    print_json(version_json_mcaffe)
    """
    new_version_json = recalculateVersion(version_json_mcaffe,"11/14/2018")
    print_json(new_version_json)
    """
    print("Loading data from csv")
    csv_json = loadCSVtoJSON("Todos_los_equipos_Peru.csv")
    csv_json = rename_data(csv_json)

    data_to_send_elk = process_data(csv_json)

    print("Sending data to ELK")
    send_to_elk(data_to_send_elk)
    print("Fin...")
    sys.exit(0)
    