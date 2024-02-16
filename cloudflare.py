#!/bin/python3
import asyncio
import aiohttp
import argparse
import re

parser = argparse.ArgumentParser(description='Set cloudflare domain dns.')

### Auth paramters
parser.add_argument('--auth-email', required=True)

# Auth token and key are mutually exclusive
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--api-token')
group.add_argument('--auth-key')

### DNS parameters
parser.add_argument('--zone-id', required=True)
parser.add_argument('--record-name', required=True)
parser.add_argument('--ttl', default=1, type=int)
parser.add_argument('--proxy', action='store_true')

### Notification parameters
parser.add_argument('--slack-webhook-url')
parser.add_argument('--slack-channel')

args = parser.parse_args()

IP_ADDR_URLS = ['https://cloudflare.com/cdn-cgi/trace', 'https://api.ipify.org', 'https://ipv4.icanhazip.com']
IPV4_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
DNS_URL_TMPL = 'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}'
DNS_PATCH_URL_TMPL = 'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
        
async def get_ip():
  async def fetch_ip(url):
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        text = await response.text()
        first_ipv4_match = re.search(IPV4_PATTERN, text)
        first_ipv4_address = first_ipv4_match.group() if first_ipv4_match else None
        return (url, first_ipv4_address)
  tasks = [fetch_ip(url) for url in IP_ADDR_URLS]

  for task in asyncio.as_completed(tasks):
      (url, result) = await task
      if result is not None:
          return result
      
async def get_dns_record(zone_id, record_name, auth_header):
  url = DNS_URL_TMPL.format(zone_id=zone_id, record_name=record_name)
  async with aiohttp.ClientSession() as session:
    async with session.get(url, headers=auth_header) as response:
      return await response.json()
    
async def set_dns_record(zone_id, record_id, record_name, auth_headers, ip, ttl, proxy):
  url = DNS_PATCH_URL_TMPL.format(zone_id=zone_id, record_id=record_id)
  data = {
    'type': 'A',
    'name': record_name,
    'content': ip,
    'ttl': ttl,
    'proxied': proxy
  }
  async with aiohttp.ClientSession() as session:
    async with session.patch(url, json=data, headers=auth_headers) as response:
        return await response.json()
    

async def send_slack_message(webhook_url, message, success=True):
    color = 'good' if success else 'danger'
    status = 'succeeded' if success else 'failed'

    payload = {
      'attachments': [{ 'color': color, 'text': message }]
    }

    async with aiohttp.ClientSession() as session:
      async with session.patch(webhook_url, json=payload) as response:
        if response.status != 200:
          print(f'Failed to send message to Slack. Status code: {response.status}')

async def send_notification(args, message, success):
  if args.slack_webhook_url:
    await send_slack_message(args.slack_webhook_url, message, success)
  # TODO: add other notification methods
      
async def main(args):
  ip = await get_ip()
  if not ip:
    await send_notification(args, 'Failed to get current ip address', False)
    return
  
  auth_headers = {'X-Auth-Email': args.auth_email}
  args.api_token and auth_headers.update({'Authorization': f'Bearer {args.api_token}'})
  args.auth_key and auth_headers.update({'X-Auth-Key': args.auth_key})
  
  dns_record = await get_dns_record(
    args.zone_id, 
    args.record_name, 
    auth_headers
  )

  if not dns_record.get('success'):
    # Convert errors to readable string
    fmt_errors = ', '.join(dns_record.get('errors', []))
    msg = 'Failed to get dns record. Errors: {fmt_errors}'.format(fmt_errors=fmt_errors)
    await send_notification(args, msg, False)
    return
  
  if dns_record.get('result_info', {}).get('count', 0) == 0:
    # TODO: Create DNS record instead of updating
    return
  
  if len(dns_record.get('result', [])) == 0 or not dns_record.get('result', [{'id': ''}])[0].get('id'):
    await send_notification(args, 'Failed to get dns record id', False)
    return
  
  record_id = dns_record.get('result')[0].get('id')
  
  if dns_record.get('result', [{'content': ''}])[0].get('content') == ip:
    # No op. Record already set to current ip
    return

  response = await set_dns_record(
    args.zone_id,
    record_id,
    args.record_name, 
    auth_headers, 
    ip, 
    args.ttl, 
    args.proxy
  )

  if not response.get('success'):
    fmt_errors = ', '.join(response.get('errors', []))
    msg = 'Failed to set dns record. Errors: {fmt_errors}'.format(fmt_errors=fmt_errors)
    await send_notification(args, msg, False)
    return
  
  old_ip = dns_record.get('result', [{'content': ''}])[0].get('content')
  await send_notification(args, 'DNS record updated: {old_ip} -> {new_ip}'.format(new_ip=ip, old_ip=old_ip), True)
  
asyncio.run(main(args))