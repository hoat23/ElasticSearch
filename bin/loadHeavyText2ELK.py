#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 29/01/2019
# Description: Code to load heavy files of text to ElasticSearch
# sys.setdefaultencoding('utf-8') #reload(sys)
#########################################################################################
from elastic import *
from utils import *
import time

nameHeavyFile = 'padron_reducido_ruc.txt'

char_sep = '|'

num_lines = 50
cont = 0
input_file = open(nameHeavyFile,'r')
while(1):
    cont = cont + 1 
    line = input_file.readline().replace('\n',"")
    if(cont==1):
        header_fields = line.split(char_sep)
    else:
        body_fields = line.split(char_sep)
        data_json = list2json(header_fields, body_fields)
        data_json.update({'rename_index':'sunat',"num_id":cont})
        try:
            if(data_json["RUC"]=="20603496842"):
                print_json(data_json)
            #send_json(data_json,IP="54.208.72.130 ",PORT=5959)
            #cont 308174  436693
        except:
            print("--> "+ str(cont))
            print(str(line))

