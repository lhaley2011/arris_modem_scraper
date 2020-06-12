
# Arris Scaper

### Pull stats from Arris Cable modem's web interface
### Send stats to InfluxDB

#### Inspired by https://github.com/andrewfraley/arris_cable_modem_stats

## measurements
- downstream
  - tags
    - modem_model
    - channel
  - fields
    - channel_id
    - status
    - frequency
    - power
    - snr
    - corrected
    - uncorrectables
- upstream
  - tags
    - modem_model
    - channel
  - fields
    - channel_id
    - status
    - symbol_rate
    - requency
    - power
- uptime
  - tags
    - modem_model
  - fields
    - uptime

## Requirements
- Python 3

## Build
- pip install -r requirements.txt
- copy .env.dist to .env
- python3 src/arris_stats.py

## Flags
- --count -n Total number of times to run (defaults to unlimited)
- --debug -d Prints excessive logs for debugging
