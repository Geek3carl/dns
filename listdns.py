#!/usr/bin/python
#*************************************************
# Description  : listdns.py
# Version	   : 1.0
# Author       : XABCLOUD.COM
#*************************************************
import sys
#-----------------VAR-----------------------------
#-----------------CLS-----------------------------
#-----------------FUN-----------------------------
def main():
	data = eval(open(sys.argv[1]).read())
	if data.has_key('records'):
		for i in data['records']:
			print str(i['id'])+"\t"+i['name']+"\t"+i['type']+"\t"+i['value']
	elif data.has_key('DomainRecords'):
		for i in data['DomainRecords']['Record']:
			print i['RR']+"\t"+i['Type']+"\t"+i['Value']
	elif data.has_key('domains'):
		for i in data['domains']:
			print i['name']
	elif data.has_key('Domains'):
		for i in data['Domains']['Domain']:
			print i['DomainName']
#-----------------PROG----------------------------
if __name__ == '__main__':
	main()
