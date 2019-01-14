#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 29/11/2018
# Description: Codigo util, para uso general
# sys.setdefaultencoding('utf-8') #reload(sys)
#########################################################################################
import sys, requests, json, csv
from datetime import datetime, timedelta
from flask import Flask, request, abort
from time import time
########################################################################################
def print_json(json_obj):
    print(json.dumps(json_obj, indent=2, sort_keys=True))
    return
#######################################################################################
def print_list(lista):
    num = 0
    for item in lista:
        print("\t{0:03d}. {1} ".format( num, item) )
        num+=1
    return
#######################################################################################
def count_elapsed_time(f,*args,**kwargs):
    """
    Decorator.
    Calculate the elapsed time of a function.
    """
    def wrapper(*args):
        start_time = time()
        ret = f(*args,**kwargs)
        elapsed_time = time() - start_time
        print("[count_elapsed_time] "+f.__name__+"Elapsed time: %0.10f seconds." % elapsed_time)
        return ret
    return wrapper
#######################################################################################
def loadCSVtoJSON(path):
    csvfile = open(path)
    data = csv.DictReader(csvfile)
    list_data = []
    
    for row in data:
        list_data.append(row)
    
    print("["+str(path)+"] -> Datos cargados:" + str(len(list_data)))
    return list_data
#######################################################################################
