#!/usr/bin/python
#-*- coding: UTF-8 -*-

import time
import datetime
import shutil
import os

import urllib2, sys, re, base64
from urlparse import urlparse
#theurl = 'http://mykyros.es:9080/stats;csv'    
theurl = 'http://192.168.24.2:9080/stats;csv'    
username = 'stats'
password = 'stats1234'
file_log_fia3 = '/var/cache/munin/www/trafico_jboss_fia3.log'
file_log_fia4 = '/var/cache/munin/www/trafico_jboss_fia4.log'
file_log_suma = '/var/cache/munin/www/trafico_jboss_suma.log'
#file_log_fia3 = './trafico_jboss_fia3.log'
#file_log_fia4 = './trafico_jboss_fia4.log'
#file_log_suma = './trafico_jboss_suma.log'

in_fia3_old = 0.0
out_fia3_old = 0.0
in_fia4_old = 0.0
out_fia4_old = 0.0

primera_vez = True 

def getstats():
    req = urllib2.Request(theurl)
    try:
        handle = urllib2.urlopen(req)
    except IOError, e:
        pass
    else:
        print "This page isn't protected by authentication."
        sys.exit(1)
    
    if not hasattr(e, 'code') or e.code != 401: 
        print "This page isn't protected by authentication."
        print 'But we failed for another reason.'
        sys.exit(1)

    authline = e.headers.get('WWW-Authenticate', '')
    #print authline
    if not authline:
        print 'A 401 error without an authentication response header - very weird.'
        sys.exit(1)
    

    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)
    try:
        handle = urllib2.urlopen(req)
    except IOError, e:
        print "It looks like the username or password is wrong."
        sys.exit(1)
    answer = handle.read()
    return answer


# Inicializar los ficheros de log
#fichero_log_fia3 = open(file_log_fia3, 'w')
#fichero_log_fia4 = open(file_log_fia4, 'w')
#fichero_log_suma = open(file_log_suma, 'w')
#fichero_log_fia3.writelines('date,in,out'+'\r\n')
#fichero_log_fia4.writelines('date,in,out'+'\r\n')
#fichero_log_suma.writelines('date,in,out'+'\r\n')
#fichero_log_fia3.close
#fichero_log_fia4.close
#fichero_log_suma.close

while True:   
    fichero_log_fia3 = open(file_log_fia3, 'a')
    fichero_log_fia4 = open(file_log_fia4, 'a')
    fichero_log_suma = open(file_log_suma, 'a')

    stats = getstats() 
    lines_stats = stats.split('\n')
    fia3_data = lines_stats[2].split(',')
    fia4_data = lines_stats[3].split(',')

    in_fia3_now = fia3_data[8]
    out_fia3_now = fia3_data[9]
    in_fia4_now = fia4_data[8]
    out_fia4_now = fia4_data[9]
    
    if (primera_vez):
        in_fia3 = 0
        out_fia3 = 0
        in_fia4 = 0
        out_fia4 = 0
        primera_vez = False
    else:
        in_fia3 = (long(in_fia3_now) - long(in_fia3_old))/100
        out_fia3 = (long(out_fia3_now) - long(out_fia3_old))/100
        in_fia4 = (long(in_fia4_now) - long(in_fia4_old))/100
        out_fia4 = (long(out_fia4_now) - long(out_fia4_old))/100
        primera_vez = False

    hora_actual = time.strftime("20%y/%m/%d %H:%M:%S", time.localtime())
    
    trama_fia3 = hora_actual+","+str(in_fia3)+","+str(out_fia3)
    trama_fia4 = hora_actual+","+str(in_fia4)+","+str(out_fia4)
    trama_suma = hora_actual+","+str(in_fia3+in_fia4)+","+str(out_fia3+out_fia4)

    #print trama_fia3
    #print trama_fia4
    #print trama_suma

    fichero_log_fia3.writelines(trama_fia3+'\r\n')
    fichero_log_fia4.writelines(trama_fia4+'\r\n')
    fichero_log_suma.writelines(trama_suma+'\r\n')

    #print str(in_fia3_now) + " - " + str(in_fia3_old) + " - " + str(in_fia3)

    in_fia3_old = in_fia3_now
    out_fia3_old = out_fia3_now
    in_fia4_old = in_fia4_now
    out_fia4_old = out_fia4_now

    fichero_log_fia3.close
    fichero_log_fia4.close
    fichero_log_suma.close

    # Si estoy al principio del dia inicalizar los logs
    str_day_now = time.strftime("%y-%m-%d", time.localtime())
    str_now = time.strftime("%H:%M:%S", time.localtime())
    str_ref1 = "23:59:48"
    str_ref2 = "23:59:59"
    date_now = datetime.datetime.strptime(str_now, '%H:%M:%S')
    date_ref1 = datetime.datetime.strptime(str_ref1, '%H:%M:%S')
    date_ref2 = datetime.datetime.strptime(str_ref2, '%H:%M:%S')
    if (date_now>date_ref1 and date_now<date_ref2):
        shutil.move('/var/cache/munin/www/trafico_jboss_fia3.log','/var/cache/munin/www/backup_logs/trafico_jboss_fia3.log.'+str_day_now)
        shutil.move('/var/cache/munin/www/trafico_jboss_fia4.log','/var/cache/munin/www/backup_logs/trafico_jboss_fia4.log.'+str_day_now)
        shutil.move('/var/cache/munin/www/trafico_jboss_suma.log','/var/cache/munin/www/backup_logs/trafico_jboss_suma.log.'+str_day_now)
        fichero_log_fia3 = open(file_log_fia3, 'w')
        fichero_log_fia4 = open(file_log_fia4, 'w')
        fichero_log_suma = open(file_log_suma, 'w')
        fichero_log_fia3.writelines('date,in,out'+'\r\n')
        fichero_log_fia4.writelines('date,in,out'+'\r\n')
        fichero_log_suma.writelines('date,in,out'+'\r\n')
        fichero_log_fia3.close
        fichero_log_fia4.close
        fichero_log_suma.close        


    time.sleep(10)


