# Dyanmic DNS Updater

This repo contains scripts to update Dynamic DNS (DDNS) service

## Native Installation

```bash
git clone https://github.com/vthurimella/DDNS.git
cd DDNS
pip install -r requirements.txt
```

## Usage
This script is used with crontab. Specify the frequency of execution through crontab.

```bash
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of the month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday 7 is also Sunday on some systems)
# │ │ │ │ │ ┌───────────── command to issue                               
# │ │ │ │ │ │
# │ │ │ │ │ │
# * * * * * /bin/bash {Location of the script}
```

### Sample Crontab
```bash
# Update Cloudflare DNS every 5 minutes
*/5 * * * * python3 ~/DDNS/cloudflare.py --auth-email {email} --api-token {api-token} --zone-id {zone-id} --record-name {record-name}
```

## Docker

### Build Image
```bash
git clone https://github.com/vthurimella/DDNS.git
docker build -t cloudflare_ddns -f Cloudflare.Dockerfile .
```

### Run Container
```bash 
docker run cloudflare_ddns --auth-email {email} --api-token {api-token} --zone-id {zone-id} --record-name {record-name}
```

### Sample Crontab
```bash
# Update Cloudflare DNS every 5 minutes
*/5 * * * * docker run cloudflare_ddns --auth-email {email} --api-token {api-token} --zone-id {zone-id} --record-name {record-name}
```

### Pre-built Image
```bash
docker pull vijaythurimella/cloudflare_ddns
docker run vijaythurimella/cloudflare_ddns --auth-email {email} --api-token {api-token} --zone-id {zone-id} --record-name {record-name}
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Reference
Some scripts were made with reference from [K0p1-Git](https://github.com/K0p1-Git/cloudflare-ddns-updater) repo.