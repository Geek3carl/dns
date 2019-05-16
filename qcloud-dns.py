#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import hashlib
import requests
import binascii
import hmac
import copy
import random
import sys
import time
from pprint import pprint
from optparse import OptionParser
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SecretId = ''
SecretKey = ''

try: import simplejson as json
except: import json

class Sign:
    def __init__(self, secretId, secretKey):
        self.secretId = secretId
        self.secretKey = secretKey

    def make(self, requestHost, requestUri, params, method = 'GET'):
        srcStr = method.upper() + requestHost + requestUri + '?' + "&".join(k.replace("_",".") + "=" + str(params[k]) for k in sorted(params.keys()))
        hashed = hmac.new(self.secretKey, srcStr, hashlib.sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]

class Request:
    timeout = 10
    version = 'Python_Tools'
    def __init__(self, secretId, secretKey):
        self.secretId = secretId
        self.secretKey = secretKey

    def send(self, requestHost, requestUri, params, files = {}, method = 'GET', debug = 0):
        params['RequestClient'] = Request.version
        params['SecretId'] = self.secretId
        sign = Sign(self.secretId, self.secretKey)
        params['Signature'] = sign.make(requestHost, requestUri, params, method)

        url = 'https://%s%s' % (requestHost, requestUri)

        if debug:
            print method.upper(), url
            print 'Request Args:'
            pprint(params)
        if method.upper() == 'GET':
            req = requests.get(url, params=params, timeout=Request.timeout,verify=False)
        else:
            req = requests.post(url, data=params, files=files, timeout=Request.timeout,verify=False)

        if debug:
            print "Response:", req.status_code, req.text
        if req.status_code != requests.codes.ok:
            req.raise_for_status()

        rsp = {}
        try:
            rsp = json.loads(req.text)
        except:
            raise ValueError, "Error: response is not json\n%s" % req.text

        code = rsp.get("code", -1)
        message = rsp.get("message", req.text)
        if rsp.get('code', -404) != 0:
            raise ValueError, "Error: code=%s, message=%s" % (code, message)
        if rsp.get('data', None) is None:
            print 'request is success.'
        else:
            print rsp['data']
def Name(name):
    up = False
    new_name = ""
    for i in name:
        if i == '_':
            up = True
            continue
        if up:
            new_name += i.upper()
        else:
            new_name += i
        up = False
    return new_name
class DNS:
    def __init__(self):
        self.params = {
                'Nonce': random.randint(1, sys.maxint),
                'Timestamp': int(time.time()),
                }
        self.files = {}
        self.host = 'cns.api.qcloud.com'
        self.uri = '/v2/index.php'
        self.method = "POST"
        self.debug = 0

    def parse_args(self):
        actions = []
        for method in dir(self):
            if method[0].isupper():
                actions.append( method )

        usage='usage: %prog Action [options]\nThis is a command line tools to access Qcloud API.\n\nSupport Actions:\n    '+"\n    ".join(actions)
        self.parser = OptionParser(usage=usage)
        from sys import argv
        if len(argv) < 2 or argv[1] not in actions:
            self.parser.print_help()
            return 0

        action = argv[1]
        self.params['Action'] = action
        usage='usage: %%prog Action [options]\n\nThis is help message for action "%s"\nMore Usage: http://www.qcloud.com/wiki/v2/%s' % (action, action)
        self.parser = OptionParser(usage=usage)
        self.parser.add_option('--debug', dest='debug', action="store_true", default=False, help='Print debug message')
        self.parser.add_option('-u', '--secret_id', dest='secret_id',default=SecretId,help='Secret ID from <https://console.qcloud.com/capi>')
        self.parser.add_option('-p', '--secret_key', dest='secret_key',default=SecretKey,help='Secret Key from <https://console.qcloud.com/capi>')
        getattr(self, action)()
        if len(argv) == 2:
            self.parser.print_help()
            return 0

        (options, args) = self.parser.parse_args() # parse again
        self.debug = options.debug
        for key in dir(options):
            if not key.startswith("__") and getattr(options, key) is None:
                raise KeyError, ('Error: Please provide options --%s' % key)


        for option in self.parser.option_list:
            opt = option.dest
            if opt not in [None, 'secret_id', 'secret_key', 'debug']:
                self.params[ Name(opt) ] = getattr(options, opt)

        self.options = options
        method = 'get_params_' + action
        if hasattr(self, method): getattr(self, method)()

        # format params
        for key, value in self.params.items():
            if value == '':
                del self.params[key]
            if isinstance(value, list):
                del self.params[key]
                for idx, val in enumerate(value):
                    self.params["%s.%s"%(key, idx)] = val

        request = Request(options.secret_id, options.secret_key)
        return request.send(self.host, self.uri, self.params, self.files, self.method, self.debug)
    def DomainList(self):
        self.parser.add_option('--length', dest='length',default=100)
    def RecordCreate(self):
        self.parser.add_option('--domain', dest='domain')
        self.parser.add_option('--subDomain', dest='subDomain')
        self.parser.add_option('--recordType', dest='recordType')
        self.parser.add_option('--recordLine', dest='recordLine',default="默认")
        self.parser.add_option('--value', dest='value')
    def RecordModify(self):
        self.parser.add_option('--domain', dest='domain')
        self.parser.add_option('--recordId', dest='recordId')
        self.parser.add_option('--subDomain', dest='subDomain')
        self.parser.add_option('--recordType', dest='recordType')
        self.parser.add_option('--recordLine', dest='recordLine',default="默认")
        self.parser.add_option('--value', dest='value')
    def RecordDelete(self):
        self.parser.add_option('--domain', dest='domain')
        self.parser.add_option('--recordId', dest='recordId')
    def RecordList(self):
        self.parser.add_option('--domain', dest='domain')
def main():
    dns = DNS()
    try:
        dns.parse_args()
    except Exception as e:
        print e
        return 1
    return 0
if __name__ == '__main__':
    sys.exit(main())
