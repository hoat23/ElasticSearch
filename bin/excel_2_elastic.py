# Codigo para subir datos del excel a elasticsearch
# Author: Deiner Zapata Silva
# Creation Date: 20/02/2021
# Last Update: 04/01/2022
# https://www.cdata.com/kb/tech/elasticsearch-odata-gsheets-apps-script.rst

#!python -m pip install pandas<=1.2
#!python -m pip install numpy==1.19.2
#!python -m pip install eland<8
#!python -m pip install elasticsearch==7.10.0
#!python -m pip install pandas<1.4

#!pip install pandas --upgrade --quiet
#!python -m pip install numpy
#!python -m pip install eland
#!python -m pip install elasticsearch
#!python -m pip install xlrd==1.2.0
#########################################################################################
from urllib.request import urlopen
def load_code_from_url(url_path):
  code_str = urlopen(url_path).read()
  code_str = code_str.decode('utf-8')
  return code_str
#########################################################################################
code_str = load_code_from_url("https://raw.githubusercontent.com/hoat23/ElasticSearch/master/bin/utils.py")
exec(code_str)
#########################################################################################
#from utils import print_json, print_list
#########################################################################################
from datetime import timezone
from urllib.request import urlopen
from elasticsearch import Elasticsearch
from eland.conftest import *
from datetime import datetime
import pandas as pd
import eland as ed
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os
from credentials import *
######################################################################################
if not ('ELASTIC' in globals()):
	from credentials import ELASTIC

CLUSTER_ENDPOINT = ELASTIC['URL']
ID = ELASTIC['ID']
API_KEY = ELASTIC['API_KEY']
######################################################################################
def get_elastic_conector(es_conector):
	if es_conector==None:
		es_conector = Elasticsearch(
		    [CLUSTER_ENDPOINT],
		    api_key=( ID , API_KEY),
		)
	print_json(es_conector.info())
	return es_conector
######################################################################################
def excel_to_pandas(excel_filename, excel_sheetname):
	xls = pd.ExcelFile(excel_filename, engine='openpyxl')# xlrd | openpyxl
	if len(excel_sheetname)==0:
		# By defaul load the first sheet in excel
		excel_sheetname = xls.sheet_names[0]
	print("\nexcel_to_pandas | filename [{0}] | sheetname [{1}]".format(excel_filename, excel_sheetname))
	df_pandas = pd.read_excel(xls, excel_sheetname)
	return df_pandas
######################################################################################
def pandas_to_eland(df_pandas,index_name, es_conector=None, es_if_exists="replace", es_refresh=True, es_type_overrides={}):
	"""
	Example: 
	es_type_overrides={
		"@timestamp": "keyword", "Apellido": "keyword", "Curso": "keyword", "DNI": "keyword",
		 "Empresa_x": "keyword", "Empresa_y": "keyword", "Fecha_Fin": "keyword",
		 "Fecha_Inicio": "keyword", "ID_Curso": "keyword", "ID_Ruta": "keyword",
		 "Menu": "keyword", "Nombre": "keyword", "Ruta de Aprendizaje": "keyword", "Telefono": "keyword"
	}
	"""
	print("\npandas_to_elasticsearch | index_name [{0}]".format(index_name))
	df_pandas = df_pandas.replace({np.NAN: None, np.inf: None})
	df_pandas = df_pandas.astype(object).where(pd.notnull(df_pandas),None)
	df_pandas.info()

	es_conector = get_elastic_conector(es_conector)

	df_eland = ed.pandas_to_eland(
	pd_df= df_pandas,
	es_client= es_conector,
	es_dest_index= index_name,
	es_type_overrides=es_type_overrides,
	es_if_exists= es_if_exists,
	es_refresh= es_refresh,
	)
	df_eland.info()
	return df_eland
######################################################################################
def excel_to_elasticsearch(excel_filename, excel_sheetname, index_name, es_conector=None):
	df_pandas = excel_to_pandas(excel_filename, excel_sheetname)
	index_name = excel_sheetname.replace("ñ","n")
	index_name =  re.sub( '[^a-zA-Z0-9\n\.]', '', index_name )
	index_name = index_name.lower()

	print("\nexcel_to_elasticsearch | index_name [{0}]".format(index_name))
	df_eland = pandas_to_eland(df_pandas, index_name, es_conector=es_conector)
	return df_eland
######################################################################################
def get_dataframe(hoja1='usuarios', hoja2='cursos', key_join='Menu', excelname='Master acceso.xls', flgtimestamp=True):
	df_users = excel_to_pandas(excelname, hoja1)
	df_cursos = excel_to_pandas(excelname, hoja2)

	print("get_dataframe | columns:{}  ".format(hoja1 ))
	print_list(list(df_users.columns), num=1)
	print("get_dataframe | columns:{}".format(hoja2 ))
	print_list(list(df_users.columns), num=1)


	#list_phones = list( df_users['Telefono'] )
	#print("get_dataframe | list_phones")
	#print_list(list_phones, sort=False)

	df_cursos.head()
	result = pd.merge(
	df_users,
	df_cursos, #([,])
	left_on = key_join,
	right_on= key_join,
	how='inner' # left, right, inner, outer
	)
	print("get_dataframe | result | head(5)")
	#result.head(5)

	if flgtimestamp:
		fecha = datetime.now().isoformat() #now(timezone.utc)
		result['@timestamp'] = "{}".format( fecha )
		print("get_dataframe | timestamp | {}".format( fecha ))
	return result
######################################################################################
if __name__=='__main__':
	print("EXCEL TO ELASTIC - SUCESS IMPORT")
	# dejarlo comentado, para importar in errores el codigo en new_message
	"""
	import json
	#Loading to Elastic
	es_conector=None
	excel_filename = 'master.xlsx'
	excel_sheetname = 'usuarios'
	df_excel = excel_to_pandas(excel_filename, excel_sheetname)
	index_name = 'database_cursosbyuser'
	#result.drop(['Empresa', 'ID_Ruta_x', 'ID_Ruta_y', 'ID_Curso'], axis='columns', inplace=True)
	#pandas_to_eland(df_result, index_name, es_conector=None, es_if_exists="replace", es_refresh=True) ##replace append
	df_excel.head()
	#json(es_connector.indices.get_mapping(index=index_name))
	"""

# Declara un objeto de la clase Bar(). En cada ciclo la barra
# muestra una porción hasta llegar a su máxima longitud en el 
# ciclo 20. La barra se representa con el carácter #

