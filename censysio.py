# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Name:     censys.py
# Purpose:  CynsysIO API Script
# By:       Ramin Asadyan
# -----------------------------------------------
 
from termcolor import colored
import argparse
import simplejson as json
import requests
import codecs
import locale
import os
import sys
import ast

# 1) Go to CENSYS.IO
# 2) SIGN UP
# 3) LOGIN
# 4) Go to 'My Account'
# 5) Copy API_ID Here in Line:		34
#		self.UID = "82ge8u9................"
# 6) Copy API SECRET Here in Line:	35
#		self.SECRET = "5uyud..............."
#
# 7) Start App ->
#		Example: python censysio.py -f 8.8.8.0/24
#
class Censys:
 
    def __init__(self, ip, p, cofetched, f_name):
        self.API_URL = "https://www.censys.io/api/v1"
        self.UID = "API_ID"
        self.SECRET = "API_SECRET"
        self.ip = ip
        self.pages = float('inf')
        self.page = p
        self.countToFetch = cofetched
        self.countOfFetched = float('0')
        self.fileName = f_name
        self.foundList = []

    def search(self):
        while self.page <= self.pages:
            params = {'query' : self.ip, 'page' : self.page}
            res = requests.post(self.API_URL + "/search/ipv4", json = params, auth = (self.UID, self.SECRET))
            payload = res.json()
            for r in payload['results']:

                ip = r["ip"]
                proto = r["protocols"]
                proto = [p.split("/")[0] for p in proto]
                proto.sort(key=float)
                protoList = ','.join(map(str, proto))
                
                if sys.platform == 'win32':
                    print '[*] IP: %s - Protocols: %s' % (ip, protoList)
                else:
                    print '[%s] IP: %s - Protocols: %s' % (colored('*', 'red'), ip, protoList)

                self.foundList.append(ip + ' ' + protoList)
                if '80' in protoList:
                    self.view(ip)

                # For limitimng fetched data
                self.countOfFetched += 1
                if self.countOfFetched >= self.countToFetch:
                    self.saveToFile()
                    exit()
                    pass

            self.pages = payload['metadata']['pages']
            self.page += 1
        self.saveToFile()

    def saveToFile(self):
        if self.fileName != '':
            if len(self.foundList) < 1:
                print "\n[*] Nothing found, '%s' not Created\n" % self.fileName
            f = open(self.fileName, 'w')
            for l in self.foundList:
                f.write(l + '\n')
            print "\n[>] Data Saved to ... %s\n" % self.fileName
            f.close()

    def view(self, server):
 
        res = requests.get(self.API_URL + ("/view/ipv4/%s" % server), auth = (self.UID, self.SECRET))
        payload = res.json()       
 
        try:
            if 'title' in payload['80']['http']['get'].keys():
                print " |  Title: %s" % payload['80']['http']['get']['title']
            if 'server' in payload['80']['http']['get']['headers'].keys():
                print " |  Server: %s" % payload['80']['http']['get']['headers']['server']
        except Exception as error:
            print error

# Start Parsing Arguments ...
parser = argparse.ArgumentParser(description = 'CENSYS.IO Search engine')
parser.add_argument('-f', '--find', help='CENSYS Search', required = True)
parser.add_argument('-p', '--page', help='Start in this page', required = False)
parser.add_argument('-c', '--count', help='Count to Fetch', required = False)
parser.add_argument('-o', '--output', help='Output File Name', required = False)

args = parser.parse_args()
ip = args.find
# Default values ...
page = 1
countToFetch = float('inf')
fname = ''

if args.page:
    page = int(args.page)

if args.count:
    countToFetch = float(args.count)
if args.output:
    fname = args.output
print "\n=================== CensysIO : Ramin Asadyan ==================="
print "[-] Search Command : %s" % ip

if args.page:
    print "[-] Start Page     : %s" % page

if args.count:
    print "[-] Count          : %s" % int(countToFetch)

if args.output:
    print "[-] File Name      : %s" % fname
print "+++++++++++++++++++++++++++ Responses +++++++++++++++++++++++++++"
censys = Censys(ip, page, countToFetch, fname)
censys.search()