# pylint: disable=line-too-long

import sys
import time
import logging
import argparse
import configparser
import requests

import config as cfg
import sb8200
import sb6190
import outputs

def main():
    """ MAIN """

    args = get_args()
    init_logger(args.debug)

    config = cfg.get_config()
    max_intervals = args.count or config['MAIN']['max_intervals'] or None
    if max_intervals:
        max_intervals = int(max_intervals)
    sleep_interval = int(config['MAIN']['sleep_interval'])
    destination = config['MAIN']['destination'].lower()
    modem_model = config['MAIN']['modem_model'].lower()

    interval_count = 0
    if not max_intervals:
        logging.info('Running for unlimited intervals')
    else:
        logging.info('Running for %d intervals', max_intervals)
    while not max_intervals or interval_count < max_intervals:
        if interval_count > 0:
            logging.info('Sleeping for %s seconds before interval %d', sleep_interval, interval_count + 1)
            sys.stdout.flush()
            time.sleep(sleep_interval)

        # Get the HTML from the modem
        html = get_html(config)
        if not html['status'] or not html['product']:
            logging.error('No HTML to parse, giving up until next interval')
            continue

        # Parse the HTML to get our stats
        if modem_model == 'sb8200':
            stats = sb8200.parse_status(html)
        elif modem_model == 'sb6190':
            stats = sb6190.parse_status(html)
        else:
            logging.error('Modem model %s not supported!  Aborting')
            sys.exit(1)

        if not stats or (not stats['upstream'] and not stats['downstream']):
            logging.error('Failed to get any stats, giving up until next interval')
            continue

        # Where should send the results?
        if destination == 'influxdb':
            outputs.send_to_influx(stats, config)
        elif destination == 'log':
            outputs.send_to_log(stats, config)
        else:
            logging.error('Destination %s not supported!  Aborting.', destination)
            sys.exit(1)
        interval_count += 1


def get_args():
    """ Get argparser args """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debug logging', action='store_true', required=False, default=False)
    parser.add_argument('-n', '--count', help='Number of intervals to run', required=False)
    args = parser.parse_args()
    return args


def get_config(config_path):
    """ Use the config parser to get the config.ini options """

    parser = configparser.ConfigParser()
    parser.read(config_path)
    return parser


def get_html(config):
    """ Get the status pages from the modem
        return the raw html
    """
    html = {}
    html['status'] = get_status_html(config)
    html['product'] = get_product_html(config)
    return html

def get_product_html(config):
    """ Get the product info page from the modem
        return the raw html
    """
    modem_url = config['MAIN']['modem_product_url']

    logging.info('Retreiving stats from %s', modem_url)

    try:
        resp = requests.get(modem_url)
        if resp.status_code != 200:
            logging.error('Error retreiving html from %s', modem_url)
            logging.error('Status code: %s', resp.status_code)
            logging.error('Reason: %s', resp.reason)
            return None
        status_html = resp.content.decode("utf-8")
        resp.close()
        return status_html
    except Exception as exception:
        logging.error(exception)
        logging.error('Error retreiving html from %s', modem_url)
        return None

def get_status_html(config):
    """ Get the status page from the modem
        return the raw html
    """
    modem_url = config['MAIN']['modem_status_url']

    logging.info('Retreiving stats from %s', modem_url)

    try:
        resp = requests.get(modem_url)
        if resp.status_code != 200:
            logging.error('Error retreiving html from %s', modem_url)
            logging.error('Status code: %s', resp.status_code)
            logging.error('Reason: %s', resp.reason)
            return None
        status_html = resp.content.decode("utf-8")
        resp.close()
        return status_html
    except Exception as exception:
        logging.error(exception)
        logging.error('Error retreiving html from %s', modem_url)
        return None



def init_logger(debug=False):
    """ Start the python logger """
    log_format = '%(asctime)s %(levelname)-8s %(message)s'

    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level, format=log_format)


if __name__ == '__main__':
    main()
