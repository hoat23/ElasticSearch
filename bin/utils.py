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
def count_elapsed_time(f):
    """
    Decorator.
    Calculate the elapsed time of a function.
    """
    def wrapper():
        start_time = time()
        ret = f()
        elapsed_time = time() - start_time
        print("Elapsed time: %0.10f seconds." % elapsed_time)
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


#######################################################################################