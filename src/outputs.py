import logging
from datetime import datetime
from pprint import pformat

def send_to_log(stats, config):
    """ Send the stats to Log """
    logging.info('Sending stats to Log')

    for stats_down in stats['downstream']:
      logging.info(" ".join(['%s=%s' % (key, value) for (key, value) in stats_down.items()]))

    for stats_up in stats['upstream']:
        logging.info(" ".join(['%s=%s' % (key, value) for (key, value) in stats_up.items()]))

    logging.info('Successfully wrote data to log')

def send_to_influx(stats, config):
    """ Send the stats to InfluxDB """
    logging.info('Sending stats to InfluxDB (%s:%s)', config['INFLUXDB']['host'], config['INFLUXDB']['port'])

    from influxdb import InfluxDBClient
    from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError

    influx_client = InfluxDBClient(
        config['INFLUXDB']['host'],
        config['INFLUXDB']['port'],
        config['INFLUXDB']['username'],
        config['INFLUXDB']['password'],
        config['INFLUXDB']['database'],
        config['INFLUXDB']['use_ssl'],
        config['INFLUXDB']['verify_ssl']
    )
    modem_model = config['MAIN']['modem_model'].lower()

    series = []
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    logging.debug('Inserting InfluxDb for time %s', current_time)

    series.append({
        'measurement': 'uptime',
        'time': current_time,
        'fields': {
            'uptime': int(stats['uptime']),
        },
        'tags': {
            'modem_model': modem_model
        }
    })

    for stats_down in stats['downstream']:
        series.append({
            'measurement': 'downstream',
            'time': current_time,
            'fields': {
                'channel_id': int(stats_down['channel_id']),
                'status': stats_down['status'],
                'frequency': float(stats_down['frequency']),
                'power': float(stats_down['power']),
                'snr': float(stats_down['snr']),
                'corrected': int(stats_down['corrected']),
                'uncorrectables': int(stats_down['uncorrectables'])
            },
            'tags': {
                'channel': int(stats_down['channel']),
                'modem_model': modem_model
            }
        })

    for stats_up in stats['upstream']:
        series.append({
            'measurement': 'upstream',
            'time': current_time,
            'fields': {
                'channel_id': int(stats_up['channel_id']),
                'status': stats_up['status'],
                'symbol_rate': int(stats_up['symbol_rate']),
                'frequency': float(stats_up['frequency']),
                'power': float(stats_up['power']),
            },
            'tags': {
                'channel': int(stats_up['channel']),
                'modem_model': modem_model
            }
        })

    try:
        influx_client.write_points(series)
    except (InfluxDBClientError, ConnectionError, InfluxDBServerError) as exception:

        # If DB doesn't exist, try to create it
        if hasattr(exception, 'code') and exception.code == 404:
            logging.warning('Database %s Does Not Exist.  Attempting to create database', config['INFLUXDB']['database'])
            try:
                influx_client.create_database(config['INFLUXDB']['database'])
                influx_client.write_points(series)
            except (InfluxDBClientError, ConnectionError, InfluxDBServerError) as exception:
                logging.error(exception)
                logging.error('Failed To Create Database or Write To New InfluxDB Database')
                return
        else:
            logging.error(exception)
            logging.error('Failed To Write To InfluxDB')
            return

    logging.info('Successfully wrote data to InfluxDB')
    logging.debug('Influx series sent to db:')
    logging.debug(pformat(series))
