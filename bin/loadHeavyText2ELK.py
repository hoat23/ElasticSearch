#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 29/01/2019
# Description: Code to load heavy files of text to ElasticSearch
# sys.setdefaultencoding('utf-8') #reload(sys)
#########################################################################################
from elastic import *
from utils import *
import re
import time
import datetime

nameHeavyFile = 'padron_reducido_ruc.txt'

char_sep = '|'

block_size = 10E6
cont = 0
input_file = open(nameHeavyFile,'rb')
print("[{0}] [START]".format(datetime.datetime.utcnow().isoformat() ) )
while(1):
    cont = cont + 1 
    try:
        line = input_file.readline()
        line = line.decode('utf-8',errors='replace')
        re.sub('[^a-zA-Z0-9-_*.]', '', line) #https://platzi.com/blog/expresiones-regulares-python/
        
        if(cont==1):
            header_fields = line.split(char_sep)
        else:
            body_fields = line.split(char_sep)
            data_json = list2json(header_fields, body_fields)
            if(len(data_json)==0):
                print("[{0}] {1}".format(datetime.datetime.utcnow().isoformat(),  cont))
            data_json.update({'rename_index':'sunat',"num_id":cont})
            #print_json(data_json)
            #send_json(data_json,IP="54.208.72.130 ",PORT=5959)
            #cont 308174  436693
        if(cont%block_size==0):
            print("[{0}] [{1}]".format(datetime.datetime.utcnow().isoformat(),cont) )
    except:
        print("[{0}] [ERROR | {1} | {2} ]".format(datetime.datetime.utcnow().isoformat(),cont) )
print("[{0}] [ END ]" + datetime.datetime.utcnow().isoformat() )