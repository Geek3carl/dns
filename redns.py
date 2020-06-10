#!/usr/bin/python
#*************************************************
# Description  : redns.py
# Help         : ./redns.py $RecordList.list $domain
# Version      : 1.0
# Author       : XABCLOUD.COM
#*************************************************
import sys
from subprocess import Popen
test
#-----------------VAR-----------------------------
fileName = sys.argv[1]
domain = sys.argv[2]
QcloudNS = set(['dnspod.net','dnsv2.com','dnsv3.com','dnsv4.com','dnsv5.com'])
AliyunNS = set(['hichina.com','alidns.com'])
NS = set()
#-----------------CLS-----------------------------
#-----------------FUN-----------------------------
def main():
	with open(fileName) as f:
		for i in f:
			l = i.strip().split()
			if l[2] == "NS":
				NS.add(l[3].split('.')[-3]+"."+l[3].split('.')[-2])
		if NS & QcloudNS:
			cmd = "./dns.sh RecordCreate "
		else:
			cmd = "./dns.sh AddDomainRecord "
	with open(fileName) as f:
		for i in f:
			l = i.strip().split()
			c = cmd+l[-3]+"."+domain+ " "+l[-2]+" "+l[-1]
			print c
			#Popen(c,shell=True)
#-----------------PROG----------------------------
if __name__ == '__main__':
	main()
