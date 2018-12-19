#!/usr/bin/env python
#coding: utf-8
########################################################################
#Programmer: Deiner Zapata Silva
#e-mail: deinerzapata@gmail.com
#Date: 13/11/2018
#https://cpiekarski.com/2011/05/09/super-easy-python-json-client-server/
#http://46.101.4.154/Artículos%20técnicos/Python/Paramiko%20-%20Conexiones%20SSH%$
#
import paramiko as pmk
import sys, json, socket, time, argparse
###############################################################################
#  VARIABLES GLOBALES
ip = port = user = passw = command = None
ip_logstash = port_logstash = None
###############################################################################
def send_json(msg, IP="0.0.0.0", PORT = 2233):
    """
        #Configuracion en /etc/logstash/conf.d/logstash-syslog.conf
        input{
            tcp{
                port => [PORT_NUMBER]
                codec => json
            }
        }
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect( (IP,PORT) )
        #print "sending message: "+str(msg)
        datajs = json.dumps(msg)
        sock.sendall( datajs.encode() )
    except:
        print("Error inesperado: "+sys.exc_info()[0])
        #sys.exit(1)
        return
    finally:
        sock.close()
        return
###############################################################################
def get_lista(lineTxt):
    Lista = lineTxt.split(" ")
    levelAux = flagMore = flagOne = 0
    newLista = []
    level = flagCommandFound = -1

    for item in Lista:
        levelAux = levelAux + 1
        if(len(item)>=2 and flagCommandFound==-1 and item!="--More--"):
            flagCommandFound = 1
        if(len(item)>0 and item!="--More--" and flagCommandFound==1):
            newLista.append(item)
            if(level==-1 or item=="\r"):
                level = levelAux
        if(flagOne==2 and flagMore==1):
            levelAux = 2
            flagMore=2
        if(1==len(item)):
            flagOne=flagOne+1
        if(item=="--More--"):
            flagMore=1    
        #print str(levelAux) +":"+str(len(item)) +">" + str(item)
    
    #print str(level) +" : "+str(newLista)
    #print str(level) +":"+str(len(item)) +">" + str(item)
    return level , newLista
###############################################################################
def process_line(lineTxt):
    command =  field = value =""
    idx_ini_01 = lineTxt.find("$ #")        # linea inicial
    idx_ini_02 = lineTxt.find("Run Time")   # linea inicial
    idx_equal = lineTxt.find("=")
    idx_michi = lineTxt.find("#")
    idx_jumpLine = lineTxt.find("\n")
    lista = []
    level = -1
    # Procesando caso especial "Backslash"
    if (len(lineTxt)!=idx_jumpLine+1):
        print("[WARNING]: proccess_line: New line : "+str(lineTxt))
        return level, lista
    # Eliminando el salto de linea al final.
    if(idx_jumpLine>=0):
        lineTxt = lineTxt[:idx_jumpLine]
    # Procesando caso especial "Primera Linea" -> "Alianza_Lima $ #config-version=FG100E-6.0.2-FW-build0163-3-180725:opmode=1:vdom=0:user=fortisiem"
    if (idx_ini_01>0):
        lista.append(lineTxt[idx_ini_01+3:idx_equal])
        lista.append(lineTxt[idx_equal+1:])
        return 1,lista
    # Procesando caso especial "Primera Linea" -> "[H[JRun Time"
    if (idx_ini_02>0):
        lista.append(lineTxt[idx_ini_02:])
        return 1,lista
    # Procesando caso general "Texto separado por espacios"-> "text1 text2 text3 ..."
    level, lista = get_lista(lineTxt)
    return level,lista
###############################################################################
def fileTXT_save(text, nameFile = "FortiConfBackup23.txt"):
    nameTempFile = nameFile[:nameFile.find(".")] + ".temp"
    ftemp = open(nameTempFile,"wb")
    ftemp.write( text )
    ftemp.close()

    # Procesando cada linea
    ftemp = open(nameTempFile,"r")
    fnew  = open(nameFile,"w")
    cont = 0
    lista_total = []
    for line in ftemp :
        level, lista = process_line(line)
        cont = cont + 1
        if(lista.__len__()>0):
            #print(">0:"+str( lista.__len__() )
            lista_total.append([lista,level])
            fnew.write(str(level)+":"+str(lista))
            fnew.write("\n")
    ftemp.close()
    fnew.close()
    # 
    return lista_total
###############################################################################
def simpleList2json(simple_lista):
    lista_json = {}
    lista_json = {'@message' : 'python test message H23' , '@tags' : ['python', 'test']}

    return lista_json
###############################################################################
def ssh_connect(IP="0.0.0.0",USER="user",PASS="pass",PORT=2233):
    try:
        ssh = pmk.SSHClient()
        ssh.set_missing_host_key_policy(pmk.AutoAddPolicy())
        ssh_stdin = ssh_stdout = ssh_sterr = None
        # "Conectandose "+USER+"@"+IP
        ssh.connect(IP , PORT , USER , PASS)
    except:
        print("[Error] : ssh_connect() : "+sys.exc_info()[0])
    finally:
        return ssh
    return
###############################################################################
def ssh_exec_command(ssh_obj,command):
    ssh_stdin = ssh_stdout = ssh_sterr = None
    input, output, error = ssh_obj.exec_command(command)
    output_txt = output.read()
    error_txt = error.read()
    return output_txt,error_txt
###############################################################################
def ssh_download_config(IP="0.0.0.0",USER="user",PASS="pass",PORT=2233):
    #http://www.unixfu.ch/diag-sys-top-2/
    ssh_obj = ssh_connect(IP,USER,PASS,PORT)
    outtxt,errortxt = ssh_exec_command(ssh_obj, "show full-configuration")
    fileTXT_save(outtxt,nameFile= time.strftime("%Y%m%d")+".txt" )
    ssh_obj.close()
    return
###############################################################################
def ssh_get_process_runing(IP="0.0.0.0",USER="user",PASS="pass",PORT=2233):
    global ip_logstash , port_logstash
    ssh_obj = ssh_connect(IP=IP,USER=USER,PASS=PASS,PORT=PORT)
    #"diagnose hardware sysinfo memory"
    outtxt,errortxt = ssh_exec_command(ssh_obj,'diag sys top-summary')# --sort=name
    print("process.....")
    print(str(errortxt))
    print("............")
    print(outtxt)
    ssh_obj.close()
    
    lista = fileTXT_save(errortxt,nameFile= "process.txt")
    lista_json = simpleList2json(lista)
    send_json(lista_json,IP=ip_logstash,PORT=port_logstash)
    
    return
###############################################################################
def execute_by_command_cmd(command):
    global ip , port , user , passw
    if(command=="check_process"):
        ssh_get_process_runing(IP=ip,USER=user,PASS=passw,PORT=port)
    if(command=="down_config"):
        ssh_download_config(IP=ip,USER=user,PASS=passw,PORT=port)
    
    return
###############################################################################
def get_parametersCMD():
    global ip , port , user , passw , command , ip_logstash , port_logstash
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip_out","--ip_out",help="IP del logstash")
    parser.add_argument("-pp_out","--pp_out",help="Puerto del logstash")
    parser.add_argument("-i","--ip",help="Direccion ip del host")
    parser.add_argument("-pp","--port",help="Puerto del host")
    parser.add_argument("-u","--user",help="Usuario SSH")
    parser.add_argument("-p","--password",help="Password SSH")
    parser.add_argument("-c","--command",help="Comando a ejecutar en la terminal [down_config,check_process]")

    args = parser.parse_args()

    if args.ip: ip = str(args.ip)
    if args.port: port = int(args.port)
    if args.user: user = str(args.user)
    if args.password: passw = str(args.password)
    if args.command: command = str(args.command)
    if args.ip_out: ip_logstash = str(args.ip_out)
    if args.pp_out: port_logstash = int(args.pp_out)

    print("Programmer : Deiner Zapata Silva")
    print("Email      : deinerzapata@gmail.com")
    
    if( ip==None or port==None or user==None or command==None):
        print("\nERROR: Faltan parametros.")
        print("ip\t= ["+str(ip)+"] \nport\t= ["+str(port)+"] \nuser\t= ["+str(user)+"] \n"+"passw\t= ["+str(passw)+"]")
        sys.exit(0)
    
    if( ip_logstash==None or port_logstash==None):
        print("\nERROR: Faltan parametros.")
        print("ip_out\t= ["+str(ip_logstash)+"]\npp_out\t= ["+str(port_logstash)+"]")
        sys.exit(0)
    
    execute_by_command_cmd(command)
    return
###############################################################################
#get_parametersCMD()
#sys.exit(0)
###############################################################################
