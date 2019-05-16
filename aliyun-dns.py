#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,os
import urllib
import requests
import base64
import hmac
import hashlib
from hashlib import sha1
import time
import uuid
import json
from optparse import OptionParser
import traceback

access_key_id = ''
access_key_secret = ''
api_server_address = 'https://alidns.aliyuncs.com'

def percent_encode(str):
    res = urllib.quote(str.decode(sys.stdin.encoding).encode('utf8'), '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res

def compute_signature(parameters, access_key_secret):
    sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])

    canonicalizedQueryString = ''
    for (k,v) in sortedParameters:
        canonicalizedQueryString += '&' + percent_encode(k) + '=' + percent_encode(v)

    stringToSign = 'GET&%2F&' + percent_encode(canonicalizedQueryString[1:])

    h = hmac.new(access_key_secret + "&", stringToSign, sha1)
    signature = base64.encodestring(h.digest()).strip()
    return signature

def compose_url(user_params):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    access_key_id = user_params['Id']
    access_key_secret = user_params['Secret']

    parameters = { \
            'Format'        : 'JSON', \
            'Version'       : '2015-01-09', \
            'AccessKeyId'   : access_key_id, \
            'SignatureVersion'  : '1.0', \
            'SignatureMethod'   : 'HMAC-SHA1', \
            'SignatureNonce'    : str(uuid.uuid1()), \
            'Timestamp'         : timestamp, \
    }

    for key in user_params.keys():
        parameters[key] = user_params[key]

    signature = compute_signature(parameters, access_key_secret)
    parameters['Signature'] = signature
    url = api_server_address + "/?" + urllib.urlencode(parameters)
    return url

def make_request(user_params, quiet=False):
    url = compose_url(user_params)
    res = requests.get(url)
    print res.text.encode('utf8')

if __name__ == '__main__':
    parser = OptionParser("%s Action=action Param1=Value1 Param2=Value2\n" % sys.argv[0])
    (options, args) = parser.parse_args()
    user_params = {}
    idx = 1
    if not sys.argv[1].lower().startswith('action='):
        user_params['action'] = sys.argv[1]
        idx = 2
    for arg in sys.argv[idx:]:
        try:
            key, value = arg.split('=',1)
            user_params[key.strip()] = value
        except ValueError, e:
            print(e.read().strip())
            raise SystemExit(e)
    make_request(user_params)
