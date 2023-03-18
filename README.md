# deflect
Caddy based visitor counter

## requirements

- Caddy https://caddyserver.com/docs
- Python/Pygtail https://pypi.org/project/pygtail/

## Running

1. prepare working directory for the script
1. configure caddyfile log path/filters and caddy start --/path/to/caddyfile
1. configure caddyfile deflect from and deflect to addresses
1. launch `visitor_counter.py`

## Reading

1. read `visitor` file to see recorded data
1. or just read the logger output of the python script
1. log format: time `unique_visitor` `total_visitor`

Config and script written for ETF QR code visitor counter

