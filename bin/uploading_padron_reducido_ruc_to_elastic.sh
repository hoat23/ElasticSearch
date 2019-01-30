#!/bin/bash
@echo off
cd
pwd
echo Downloading padron_reducido from SUNAT
wget http://www2.sunat.gob.pe/padron_reducido_ruc.zip -O /tmp/padron_reducido_ruc.zip
echo Unzip padron_reducido_ruc.zip a padron_reducido_ruc.txt
unzip -o /tmp/padron_reducido_ruc.zip -d /usr/share/logstash/
echo Uploading to Elastic
python /usr/share/logstash/loadHeavyText2ELK.py
echo Fin