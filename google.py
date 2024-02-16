#!/bin/python3
import argparse
import base64
import requests

parser = argparse.ArgumentParser(description='Set google domain dns.')
parser.add_argument('--domain', required=True)
parser.add_argument('--user', required=True)
parser.add_argument('--password', required=True)

args = parser.parse_args()
s_tok = '{user}:{password}'.format(user=args.user, password=args.password)
b64_bytes = base64.b64encode(s_tok.encode('ascii'))
b64_tok = b64_bytes.decode("ascii")

url = 'https://domains.google.com/nic/update?hostname={domain}'.format(domain=args.domain)

payload={}
headers = { 'Authorization': 'Basic {tok}'.format(tok=b64_tok) }

response = requests.request('POST', url, headers=headers, data=payload)

print(response.text)
