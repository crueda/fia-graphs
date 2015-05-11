#!/usr/bin/python
#-*- coding: UTF-8 -*-

import time
import datetime
import shutil
import os

import urllib2, sys, re, base64
from urlparse import urlparse
#theurl = 'http://mykyros.es:9080/stats;csv'    
theurl = 'http://192.168.24.3:9080/stats;csv'    
username = 'stats'
password = 'stats1234'
file_log_gprs = '/var/cache/munin/www/trafico_gprs.log'



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


while True:   
    fichero_log_gprs = open(file_log_gprs, 'a')
    
    stats = getstats() 
    lines_stats = stats.split('\n')

    gprs_data = lines_stats[1].split(',')

    n_gprs_now = gprs_data[4]



    hora_actual = time.strftime("20%y/%m/%d %H:%M:%S", time.localtime())
    
    trama_gprs = hora_actual+","+str(n_gprs_now)
    #print trama_gprs

    fichero_log_gprs.writelines(trama_gprs+'\r\n')

    fichero_log_gprs.close

    # Si estoy al principio del dia inicalizar los logs
    str_day_now = time.strftime("%y-%m-%d", time.localtime())
    str_now = time.strftime("%H:%M:%S", time.localtime())
    str_ref1 = "23:59:48"
    str_ref2 = "23:59:59"
    date_now = datetime.datetime.strptime(str_now, '%H:%M:%S')
    date_ref1 = datetime.datetime.strptime(str_ref1, '%H:%M:%S')
    date_ref2 = datetime.datetime.strptime(str_ref2, '%H:%M:%S')
    if (date_now>date_ref1 and date_now<date_ref2):
        shutil.move('/var/cache/munin/www/trafico_gprs.log','/var/cache/munin/www/backup_logs/trafico_gprs.log.'+str_day_now)
        fichero_log_gprs = open(file_log_gprs, 'w')
        fichero_log_gprs.writelines('date,GPRS connections'+'\r\n')
        fichero_log_gprs.close        


    time.sleep(10)


