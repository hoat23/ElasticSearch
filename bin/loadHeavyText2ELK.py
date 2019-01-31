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
def loadHeavyText2ELK(nameHeavyFile, char_sep = '|',block_size = 1E4,send_elk=False):
    cont = 0
    input_file = open(nameHeavyFile,'rb')
    print("[{0} | START ]".format(datetime.datetime.utcnow().isoformat() ) )
    block_data=[]
    elk = elasticsearch()
    sum_chars = critical_err = 0
    header_line = ""
    while(1):
        cont = cont + 1 
        try:
            line = input_file.readline()
            org_line = line = line.decode('utf-8',errors='replace')
            sum_chars =  sum_chars + len(line)
            line = line.replace("\n","")
            line = line.replace("\r","")
            #line = line.replace("\\||","-|")
            line = line.replace("\\","-")
            line = line.replace("||","|")
            
            re.sub('[^a-zA-Z0-9-_*.]', '', line) #https://platzi.com/blog/expresiones-regulares-python/
            
            if(cont==1):
                header_line = org_line
                header_fields = line.split(char_sep)
            else:
                data_json = {}
                body_fields = line.split(char_sep)
                data_json, err = list2json(header_fields, body_fields,return_err=True)    
                if(err!=0):
                    print("[{0} | ERROR | num line : {1: 10d} | num byte : {2: 10d}]".format(datetime.datetime.utcnow().isoformat(), cont, sum_chars) )
                    print(" ->  | {0}".format(header_line))
                    print(" ->  | {0}".format(org_line))
                    print(" ->  | {0}".format(line))
                    beep_alert()

                if(len(data_json)==0):
                    print("[{0} | ERROR |* data lost * | num line : {1: 10d} | num byte : {2: 10d}]".format(datetime.datetime.utcnow().isoformat(), cont, sum_chars) )
                    print(" ->  | {0}".format(header_line))
                    print(" ->  | {0}".format(org_line))
                    print(" ->  | {0}".format(line))
                    beep_alert()
                else:
                    data_json.update({'rename_index':'sunat',"source_id":cont})
                    #send_json(data_json,IP="54.208.72.130 ",PORT=5959)#print_json(data_json)
                    block_data.append(data_json)
                
                if(len(body_fields)==0):
                    critical_err = critical_err + 1
                    print("[{0} | CRIT  | num line : {1: 10d} | num byte : {2: 10d}]".format(datetime.datetime.utcnow().isoformat(), critical_err) )
                
            if(cont%block_size==0):
                print("[{0} | INFO  | num line : {1: 10d}]".format(datetime.datetime.utcnow().isoformat(), cont) )
                if(send_elk):
                    elk.post_bulk(block_data,header_json={"index":{"_index":"sunat","_type":"_doc"}})
                block_data=[]
                #time.sleep(1)
        except:
            print("[{0} | ERROR | {1} ]".format(datetime.datetime.utcnow().isoformat(), cont) )
            print(" ->  | {0}".format(header_line))
            print(" ->  | {0}".format(org_line))
            print(" ->  | {0}".format(line))
            beep_alert(t=500,count=3)
            critical_err = critical_err + 1
            #break
        finally:
            if(critical_err>20):
                print("[{0} | CRIT  | {1} ]".format(datetime.datetime.utcnow().isoformat(), critical_err) )
                beep_alert(t=500,count=3)
                break
    print("[{0} | END   ]".format(datetime.datetime.utcnow().isoformat()))
#########################################################################################
if __name__ == "__main__":
    if (p.system()=='Windows'):# ONLY WINDOWS
        full_path='padron_reducido_ruc.txt'
    else:
        full_path='/usr/share/logstash/padron_reducido_ruc.txt'
    loadHeavyText2ELK(full_path, send_elk=False)
