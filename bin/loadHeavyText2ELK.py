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
import platform as p
#########################################################################################
if (p.system()=='Windows'):# ONLY WINDOWS
    import winsound 
#########################################################################################
def beep_alert(f = 2500, t = 1000, count = 1):
    if (p.system()=='Windows'):# ONLY WINDOWS
        for i in range(0,count):
            winsound.Beep(f,t)
    return
#########################################################################################
def loadHeavyText2ELK(nameHeavyFile = 'padron_reducido_ruc.txt',char_sep = '|',block_size = 1E4,send_elk=False):
    cont = 0
    input_file = open(nameHeavyFile,'rb')
    print("[{0} | START ]".format(datetime.datetime.utcnow().isoformat() ) )
    block_data=[]
    elk = elasticsearch()
    sum_chars = critical_err = 0
    while(1):
        cont = cont + 1 
        try:
            line = input_file.readline()
            line = line.decode('utf-8',errors='replace')
            sum_chars =  sum_chars + len(line)
            line = line.replace("\n","")
            line = line.replace("\r","")
            re.sub('[^a-zA-Z0-9-_*.]', '', line) #https://platzi.com/blog/expresiones-regulares-python/
            
            if(cont==1):
                header_fields = line.split(char_sep)
            else:
                data_json = {}
                body_fields = line.split(char_sep)
                data_json = list2json(header_fields, body_fields)    
                if(len(data_json)==0 or len(body_fields)==0):
                    print("[{0} | ERROR | num line : {1: 10d} | num byte : {2: 10d}]".format(datetime.datetime.utcnow().isoformat(), cont, sum_chars) )
                    beep_alert()
                    if(len(body_fields)==0):
                        critical_err = critical_err + 1
                else:
                    data_json.update({'rename_index':'sunat',"source_id":cont})
                    #print_json(data_json)
                    #send_json(data_json,IP="54.208.72.130 ",PORT=5959)
                    #cont 308174  436693
                    block_data.append(data_json)
            if(cont%block_size==0):
                if(send_elk):
                    elk.post_bulk(block_data,header_json={"index":{"_index":"sunat","_type":"_doc"}})
                else:
                    print("[{0} | INFO  | num line : {1: 10d}]".format(datetime.datetime.utcnow().isoformat(), cont) )
                block_data=[]
                time.sleep(1)
        except:
            print("[{0} | ERROR | {1} ]".format(datetime.datetime.utcnow().isoformat(), cont) )
            break
        finally:
            if(critical_err>5):
                print("[{0} | CRIT  | {1} ]".format(datetime.datetime.utcnow().isoformat(), critical_err) )
                break
    print("[{0} | END   ]".format(datetime.datetime.utcnow().isoformat()))
#########################################################################################
if __name__ == "__main__":
    loadHeavyText2ELK()