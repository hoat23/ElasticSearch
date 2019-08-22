#coding: UTF-8 
#########################################################################################
# Developer: Deiner Zapata Silva.
# Date: 27/05/2019
# Last update: 21/08/2019
# Description: Server to send emails using gmail account.
# Notas: https://pypi.org/project/imgkit/
#########################################################################################
import smtplib, imghdr, os
from email.message import EmailMessage
from credentials import *
from utils import *
from utils_elk import *
#########################################################################################
EMAIL_ADDRESS = "{0}@{1}".format( USER_G, DOMINIO)
EMAIL_PASSWORD = "{0}".format( PASS_G )
#########################################################################################
def build_email(email_to_send=["deiner.zapata@supra.com.pe"], 
                email_subject="[H23] You are awesome :-)", 
                email_body={"text":"Writting from your desktop.",
                            "files":["gato.jpg"],
                            "alternative": "siem_format.html"
                            }):

    msg = EmailMessage()
    msg['Subject'] = email_subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ','.join(email_to_send)
    try:
        msg.set_content(email_body['text'])
    except:
        pass
    file_name = "defaul.jpg"
    file_alternative = "default.html"
    try:
        var_template = email_body['alternative']
        file_type = "html"
        if var_template.find('.html')>0 and len(var_template)<32:
            try: 
                file_alternative = email_body['alternative']
                if (file_alternative.find(".html")>=0):
                    with open(file_alternative, 'r') as f:
                        file_data = f.read()
                    msg.add_alternative(file_data, subtype=file_type)
                else:
                    print("| INFO|  build_email| Falta implementar")
                
            except:
                print("| ERROR| build_email | Error cargando <{0}>".format(file_alternative))
        else:
            msg.add_alternative(var_template, subtype=file_type)
    except:
        print("| INFO|  build_email| Falta implementar")
        pass
    try:
        for one_file in email_body['files']:
            try: 
                file_name = one_file
                with open(file_name, 'rb') as f:
                    file_data = f.read()
                    file_type = imghdr.what(f.name)
                msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
            except:
                print("| ERROR |build_email | Error cargando archivo <{0}>".format(file_name))
    except:
        #print("| INFO|  build_email| Falta implementar")
        pass
    return msg
#########################################################################################
def send_email(message):
    #message = build_email()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)
        smtp.quit()
        print("finn")
    print('INFO| send_email() | Everything is right :-).')
    return 
#########################################################################################
def build_and_send_email_simple():
    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = '[H23] You are awesome--- :-)'
        body = 'Writting from your desktop.'
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(EMAIL_ADDRESS, 'deiner.zapata@supra.com.pe', msg)
    return
#########################################################################################
def build_template_by_incidencia(one_doc, siem_incidencias,save_template=False, data_adicional=[]):
    # name source severity
    # description
    # inicio last duration
    # client sede reporting_ip
    # incident_notification incident_target id
    var_html = ""
    for data_html in data_adicional:
        var_html = var_html + data_html + "<br>"

    template_with_fields_updated = {
        "fields": {
            "subject": "{0} [{1}] - {2}".format(   siem_incidencias["rule_name"] , one_doc["_source"]["cmdb"]["client"], siem_incidencias["subject"] ),
            "__incident_status_value": "{0} [{1}] - {2}".format(   siem_incidencias["rule_name"] , one_doc["_source"]["cmdb"]["client"], siem_incidencias["subject"]),
            "incident_status_value": one_doc["_source"]['incidencia_status']['value'],
            "rule_name": siem_incidencias['rule_name'],
            "rule_description": siem_incidencias['rule_description'],
            "incident_id": one_doc["_source"]['incidencia_id'],
            "incident_severity_category": siem_incidencias['severity_category'],
            "incident_severity": siem_incidencias['severity'],
            "first_run": one_doc["_source"]['incidencia_status']['first_run'],
            "last_run": one_doc["_source"]['incidencia_status']['last_run'],
            "duration": " hrs",
            "cmdb_client": one_doc["_source"]['cmdb']['client'],
            "cmdb_sede": one_doc["_source"]['cmdb']['sede'],
            "cmdb_reporting_ip": one_doc["_source"]['cmdb']['reporting_ip'],
            "incident_source": "{0} | {1}".format(one_doc["_source"]["cmdb"]["reporting_ip"], siem_incidencias['incident_source']),#one_doc["_source"]['array_doc_id'],
            "count": "count",
            "link_to_kibana": "link_to_kibana",
            "notification_recipients": siem_incidencias['recipients']['emails'],
            "more_detail": var_html,
            "cleared_reason": "cleared_reason",
            "incident_detail": "incident_detail",
            "rule_remediation": "rule_remediation",
            "incident_target": siem_incidencias['incident_target']
        },
        "file_html": "tmplt_incidencia_001.html"
    }
    file_template = load_template(template_with_fields_updated, save_file=save_template)
    #print_json(template_with_fields_updated)
    return file_template
#########################################################################################
def send_email_by_watcher(data_json):
    message = build_email(
                email_to_send=data_json['recipients'], 
                email_subject=data_json['subject'], 
                email_body=data_json['email_body'])
    send_email(message)
#########################################################################################
def send_email_by_incidencia(incidencia,data_adicional):
    siem_incidencia = get_incidencia(incidencia["_source"]["incidencia_type"])
    
    try:
        texto = siem_incidencia['subject_email']['text']
        fields = siem_incidencia['subject_email']['fields']
        #print("DBG |send_email_by_incidencia | texto={0} | fields={1}".format(texto, fields))
        temp = "\"{0}\".format({1})".format(  texto, (",". join(fields)) )
        print("DBG |{0}".format(temp)) 
        #subject_str =  eval( temp )
        subject_str = "{0} |{1}| {2}".format(siem_incidencia['rule_name'],incidencia['_source']['cmdb']['client'],siem_incidencia['subject'])
    except:
        subject_str = "ID:{3:05d} | {0} | {1} | {2} ".format(   siem_incidencia["rule_name"] , incidencia["_source"]["cmdb"]["client"], siem_incidencia["subject"] , incidencia['_source']['incidencia_id'])
    finally:
        file_template = build_template_by_incidencia(incidencia, siem_incidencia, save_template=False, data_adicional=data_adicional)
        message = build_email(
                    email_to_send=siem_incidencia['recipients']['emails'], 
                    email_subject=subject_str, 
                    email_body={
                        "text": siem_incidencia['subject'] ,
                        "alternative": file_template
                        })
        send_email(message)
        return
#########################################################################################
def testing_template():
    print("[INFO ] testing_template()")
    #THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    one_doc = {
        "_index" : "incidencias",
        "_type" : "_doc",
        "_source" : {
            "servicio" : "heartbeat_FIBERTEL_8.8.8.8",
            "debug" : {
                "flagInciIdxFound" : True
            },
            "incidencia_type" : "network_device_status",
            "incidencia_status" : {
                "last_run" : "2019-05-28T21:30:28.143Z",
                "value" : "open",
                "first_run" : "2019-05-28T17:06:28.426Z"
            },
            "incidencia_id" : 636,
            "cmdb" : {
                "cluster_name" : "FIBERTEL",
                "marca" : "Fortinet",
                "ip_group" : "Public IP",
                "sede" : "None",
                "categoria" : "Firewall",
                "client" : "FIBERTEL",
                "model" : "FortiGate 50E",
                "hash" : "TqShqqJMkQIuI/PHmTirMcucNa8=",
                "reporting_ip" : "8.8.8.8"
            },
            "array_doc_id" : [
                "178"
            ]
        },
        "_id" : "636",
        "sort" : [
        1559079028143
        ],
        "_score" : None
    }
    
    siem_incidencia = get_incidencia(one_doc["_source"]["incidencia_type"])
    file_template = build_template_by_incidencia(one_doc, siem_incidencia, save_template=True)
    return
#########################################################################################
if __name__ == "__main__":
    print("[INFO ] Ejecutando <server_gmail.py>")
    #send_email()
    testing_template()
    pass
