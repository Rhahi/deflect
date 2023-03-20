# deflect
Caddy based visitor counter

## requirements

- Caddy https://caddyserver.com/docs
- Python/Pygtail https://pypi.org/project/pygtail/

## Running

1. prepare working directory for the script
1. configure caddyfile log path/filters and caddy start --config /path/to/caddyfile
1. configure caddyfile deflect from and deflect to addresses
1. install deflect by using `pip install .`
1. launch `python3 -m deflect` while in the directory where visitorfile.html and access.log will be present. Otherwise, provide them via args.

## Reading

1. read `visitorfile.html` file to see recorded data
1. or just read the logger output of the python script
1. log format: timestamp,today_unique_visitors,today_total_visitors,total_visitors,unique_visitors,

Config and script written for ETF QR code visitor counter

